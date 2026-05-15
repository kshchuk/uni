// Command supervisor is the GUI entry point of the lab.  It creates a
// System V shared memory segment, spawns process_a and process_b as
// children, exposes controls (sliders, buttons, bank initial values) and
// renders the live state of the machine (bank counts, Dekker flags,
// metrics, event log).
package main

import (
	"context"
	"fmt"
	"io"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"syscall"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/data/binding"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/widget"

	"lab3/internal/coinbank"
	"lab3/internal/dekker"
	"lab3/internal/ipc"
	"lab3/internal/shm"
)

const maxLogLines = 200

type supervisor struct {
	seg     *shm.Segment
	state   *shm.State
	procA   *exec.Cmd
	procB   *exec.Cmd
	logMu   sync.Mutex
	logLines []string
	logBind binding.String

	bankBindings  [6]binding.String
	flagC1        binding.String
	flagC2        binding.String
	flagTurn      binding.String
	metricsA      binding.String
	metricsB      binding.String
	collisions    binding.String
	statusBinding binding.String
	autoCheck     *widget.Check
	sliderA       *widget.Slider
	sliderB       *widget.Slider
	delayLabelA   *widget.Label
	delayLabelB   *widget.Label
}

func main() {
	captureMode := os.Getenv("LAB3_CAPTURE") != ""

	a := app.New()
	w := a.NewWindow("Lab 3 — Автомат розміну (Деккер, " + dekker.Mode + ")")
	w.Resize(fyne.NewSize(900, 720))
	if captureMode {
		w.CenterOnScreen()
	} else {
		w.SetFixedSize(true)
		w.CenterOnScreen()
	}
	setWindowTitle := func(shmID int) {
		w.SetTitle(fmt.Sprintf("Lab 3 — Автомат розміну (Деккер, %s) SHM=%d", dekker.Mode, shmID))
	}

	sv := &supervisor{
		logBind:       binding.NewString(),
		flagC1:        binding.NewString(),
		flagC2:        binding.NewString(),
		flagTurn:      binding.NewString(),
		metricsA:      binding.NewString(),
		metricsB:      binding.NewString(),
		collisions:    binding.NewString(),
		statusBinding: binding.NewString(),
	}
	for i := range sv.bankBindings {
		sv.bankBindings[i] = binding.NewString()
	}
	sv.setStatus("Ініціалізація…")

	if err := sv.bootstrap(); err != nil {
		dialog.ShowError(err, w)
	} else {
		setWindowTitle(sv.seg.ID)
	}

	w.SetContent(sv.buildUI(w))

	w.SetCloseIntercept(func() {
		sv.shutdown()
		w.Close()
	})

	go sv.poll(context.Background())

	go func() {
		sigc := make(chan os.Signal, 1)
		signal.Notify(sigc, syscall.SIGINT, syscall.SIGTERM)
		<-sigc
		sv.shutdown()
		os.Exit(0)
	}()

	if captureMode {
		go func() {
			time.Sleep(900 * time.Millisecond)
			fyne.Do(func() { w.SetFullScreen(true) })
		}()
	}

	w.ShowAndRun()
}

// bootstrap creates the SHM segment, initialises the bank with default
// values and starts the two worker processes.
func (s *supervisor) bootstrap() error {
	seg, err := shm.Create()
	if err != nil {
		return fmt.Errorf("create SHM: %w", err)
	}
	s.seg = seg
	s.state = seg.State

	defaultBank := [6]int32{50, 25, 20, 15, 10, 5}
	for i, v := range defaultBank {
		atomic.StoreInt32(&s.state.Bank[i], v)
	}
	atomic.StoreInt32(&s.state.Turn, dekker.ProcA)
	atomic.StoreInt32(&s.state.DelayMsA, 250)
	atomic.StoreInt32(&s.state.DelayMsB, 250)

	procABin, procBBin, err := workerBinaries()
	if err != nil {
		return err
	}

	s.procA, err = s.spawn(procABin, "A")
	if err != nil {
		return fmt.Errorf("spawn process_a: %w", err)
	}
	s.procB, err = s.spawn(procBBin, "B")
	if err != nil {
		return fmt.Errorf("spawn process_b: %w", err)
	}
	s.setStatus("Процеси A і B запущені, SHM id=" + strconv.Itoa(s.seg.ID))
	s.appendLog(fmt.Sprintf("[supervisor] mode=%s SHM id=%d", dekker.Mode, s.seg.ID))
	if path := os.Getenv("LAB3_SHM_ID_FILE"); path != "" {
		_ = os.WriteFile(path, []byte(strconv.Itoa(s.seg.ID)), 0o644)
	}
	return nil
}

func (s *supervisor) spawn(bin, label string) (*exec.Cmd, error) {
	cmd := exec.Command(bin)
	cmd.Env = append(os.Environ(), "LAB3_SHM_ID="+strconv.Itoa(s.seg.ID))
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, err
	}
	cmd.Stderr = os.Stderr
	if err := cmd.Start(); err != nil {
		return nil, err
	}
	go s.consumeEvents(stdout, label)
	return cmd, nil
}

// workerBinaries locates the freshly built worker binaries.  They are
// expected to sit next to the supervisor binary (typical when invoked
// from `make run`) or under ./bin when running from go run.
func workerBinaries() (string, string, error) {
	exe, err := os.Executable()
	if err != nil {
		return "", "", err
	}
	dir := filepath.Dir(exe)
	wd, _ := os.Getwd()
	candidates := []string{dir, filepath.Join(dir, "..", "bin"), filepath.Join(wd, "bin"), "bin"}
	procA := ""
	procB := ""
	for _, d := range candidates {
		a := filepath.Join(d, "process_a")
		b := filepath.Join(d, "process_b")
		if procA == "" {
			if _, err := os.Stat(a); err == nil {
				procA = a
			}
		}
		if procB == "" {
			if _, err := os.Stat(b); err == nil {
				procB = b
			}
		}
		if procA != "" && procB != "" {
			break
		}
	}
	if procA == "" || procB == "" {
		return "", "", fmt.Errorf("worker binaries not found near %s (expected ./process_a and ./process_b)", dir)
	}
	return procA, procB, nil
}

func (s *supervisor) consumeEvents(r io.Reader, label string) {
	reader := ipc.NewReader(r)
	for {
		ev, err := reader.Next()
		if err == io.EOF {
			s.appendLog(fmt.Sprintf("[%s] EOF", label))
			return
		}
		if err != nil {
			s.appendLog(fmt.Sprintf("[%s] read err: %v", label, err))
			return
		}
		s.appendLog(formatEvent(ev))
	}
}

func formatEvent(ev ipc.Event) string {
	ts := time.Unix(0, ev.TS).Format("15:04:05.000")
	pieces := []string{ts, ev.Process, string(ev.Kind)}
	if ev.Coin != 0 {
		pieces = append(pieces, fmt.Sprintf("coin=%d", ev.Coin))
	}
	if ev.Denom != 0 {
		pieces = append(pieces, fmt.Sprintf("denom=%d", ev.Denom))
	}
	if ev.Count != 0 {
		pieces = append(pieces, fmt.Sprintf("count=%d", ev.Count))
	}
	if ev.Refuse != 0 {
		pieces = append(pieces, fmt.Sprintf("refuse=%d (%s)", ev.Refuse, coinbank.RefuseText(ev.Refuse)))
	}
	if ev.Mode != "" {
		pieces = append(pieces, "mode="+ev.Mode)
	}
	if ev.Message != "" {
		pieces = append(pieces, ev.Message)
	}
	return strings.Join(pieces, " ")
}

func (s *supervisor) appendLog(line string) {
	s.logMu.Lock()
	s.logLines = append(s.logLines, line)
	if len(s.logLines) > maxLogLines {
		s.logLines = s.logLines[len(s.logLines)-maxLogLines:]
	}
	rendered := strings.Join(s.logLines, "\n")
	s.logMu.Unlock()
	s.logBind.Set(rendered)
}

func (s *supervisor) setStatus(text string) { s.statusBinding.Set(text) }

func (s *supervisor) poll(ctx context.Context) {
	ticker := time.NewTicker(80 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			s.refreshFromState()
		}
	}
}

func (s *supervisor) refreshFromState() {
	st := s.state
	if st == nil {
		return
	}
	for i, denom := range shm.BankDenominations {
		v := atomic.LoadInt32(&st.Bank[i])
		s.bankBindings[i].Set(fmt.Sprintf("%2d коп. × %d", denom, v))
	}
	s.flagC1.Set(fmt.Sprintf("C1 = %d", atomic.LoadInt32(&st.C1)))
	s.flagC2.Set(fmt.Sprintf("C2 = %d", atomic.LoadInt32(&st.C2)))
	turn := atomic.LoadInt32(&st.Turn)
	turnLabel := "A"
	if turn == dekker.ProcB {
		turnLabel = "B"
	}
	s.flagTurn.Set(fmt.Sprintf("Turn = %d (%s)", turn, turnLabel))

	s.metricsA.Set(fmt.Sprintf(
		"A: entered=%d busy=%d wait=%.1fms last_coin=%d",
		atomic.LoadInt64(&st.EnterA),
		atomic.LoadInt64(&st.BusyA),
		float64(atomic.LoadInt64(&st.WaitNsA))/1e6,
		atomic.LoadInt32(&st.LastA),
	))
	lastB := atomic.LoadInt32(&st.LastB)
	lastSummary := ""
	if lastB == 0 {
		if c := atomic.LoadInt32(&st.LastCoin); c != 0 {
			lastSummary = fmt.Sprintf("DEAL coin=%d -> %d×%d", c, atomic.LoadInt32(&st.LastCount), atomic.LoadInt32(&st.LastDenom))
		}
	} else {
		lastSummary = fmt.Sprintf("REFUSE %d (%s)", lastB, coinbank.RefuseText(lastB))
	}
	s.metricsB.Set(fmt.Sprintf(
		"B: entered=%d busy=%d wait=%.1fms %s",
		atomic.LoadInt64(&st.EnterB),
		atomic.LoadInt64(&st.BusyB),
		float64(atomic.LoadInt64(&st.WaitNsB))/1e6,
		lastSummary,
	))
	collisions := atomic.LoadInt32(&st.Collisions)
	maxInCS := atomic.LoadInt32(&st.MaxInCS)
	collText := fmt.Sprintf("Колізій у КД: %d (max в КД: %d)", collisions, maxInCS)
	if collisions > 0 {
		collText = "!! " + collText + " — взаємовиключення ПОРУШЕНЕ"
	}
	s.collisions.Set(collText)

	if s.autoCheck != nil {
		want := atomic.LoadInt32(&st.AutoMode) == 1
		if s.autoCheck.Checked != want {
			fyne.Do(func() { s.autoCheck.SetChecked(want) })
		}
	}
	s.syncDelaySlider(s.sliderA, s.delayLabelA, atomic.LoadInt32(&st.DelayMsA), "A")
	s.syncDelaySlider(s.sliderB, s.delayLabelB, atomic.LoadInt32(&st.DelayMsB), "B")
}

func (s *supervisor) syncDelaySlider(sl *widget.Slider, lbl *widget.Label, ms int32, proc string) {
	if sl == nil || lbl == nil {
		return
	}
	v := float64(ms)
	if int(sl.Value+0.5) == int(v+0.5) {
		want := fmt.Sprintf("Затримка %s: %d мс", proc, ms)
		if lbl.Text != want {
			fyne.Do(func() { lbl.SetText(want) })
		}
		return
	}
	fyne.Do(func() {
		sl.SetValue(v)
		lbl.SetText(fmt.Sprintf("Затримка %s: %d мс", proc, ms))
	})
}

func (s *supervisor) buildUI(parent fyne.Window) fyne.CanvasObject {
	// --- Bank initial values (top-left) ---
	bankInputs := make([]*widget.Entry, 6)
	bankBox := container.NewVBox(widget.NewLabelWithStyle("Банк монет (початкові)", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}))
	for i, denom := range shm.BankDenominations {
		e := widget.NewEntry()
		e.SetText(strconv.Itoa(int(atomic.LoadInt32(&s.state.Bank[i]))))
		bankInputs[i] = e
		bankBox.Add(container.NewHBox(widget.NewLabel(fmt.Sprintf("%2d коп.:", denom)), e))
	}
	applyBank := widget.NewButton("Записати початковий банк", func() {
		for i, e := range bankInputs {
			v, err := strconv.Atoi(strings.TrimSpace(e.Text))
			if err != nil || v < 0 {
				dialog.ShowError(fmt.Errorf("неправильне значення у полі %d коп.", shm.BankDenominations[i]), parent)
				return
			}
			atomic.StoreInt32(&s.state.Bank[i], int32(v))
		}
		s.appendLog("[supervisor] банк перезаписано з GUI")
	})
	bankBox.Add(applyBank)

	// --- Live bank panel ---
	liveBox := container.NewVBox(widget.NewLabelWithStyle("Поточний банк", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}))
	for i := range shm.BankDenominations {
		liveBox.Add(widget.NewLabelWithData(s.bankBindings[i]))
	}

	// --- Dekker flags + metrics panel ---
	metricsLabel := func(b binding.String) *widget.Label {
		l := widget.NewLabelWithData(b)
		l.Wrapping = fyne.TextWrapWord
		return l
	}
	dekkerBox := container.NewVBox(
		widget.NewLabelWithStyle("Флаги Деккера", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}),
		widget.NewLabelWithData(s.flagC1),
		widget.NewLabelWithData(s.flagC2),
		widget.NewLabelWithData(s.flagTurn),
		widget.NewSeparator(),
		widget.NewLabelWithStyle("Метрики", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}),
		metricsLabel(s.metricsA),
		metricsLabel(s.metricsB),
		metricsLabel(s.collisions),
	)

	// --- Bottom controls ---
	denomEntry := widget.NewSelect([]string{"1", "2", "5", "10", "25", "50"}, nil)
	denomEntry.SetSelected("1")

	insertBtn := widget.NewButton("Вкинути монету (A)", func() {
		atomic.StoreInt32(&s.state.CmdInsert, 1)
		s.appendLog("[supervisor] -> A: insert")
	})
	requestBtn := widget.NewButton("Розміняти (B)", func() {
		val, err := strconv.Atoi(denomEntry.Selected)
		if err != nil {
			dialog.ShowError(err, parent)
			return
		}
		atomic.StoreInt32(&s.state.CmdDenom, int32(val))
		atomic.StoreInt32(&s.state.CmdRequest, 1)
		s.appendLog(fmt.Sprintf("[supervisor] -> B: request denom=%d", val))
	})

	autoCheck := widget.NewCheck("Auto-режим (стрес-тест)", func(on bool) {
		v := int32(0)
		if on {
			v = 1
		}
		atomic.StoreInt32(&s.state.AutoMode, v)
		s.appendLog(fmt.Sprintf("[supervisor] auto-mode=%v", on))
	})
	s.autoCheck = autoCheck

	sliderA := widget.NewSlider(0, 500)
	sliderA.SetValue(float64(atomic.LoadInt32(&s.state.DelayMsA)))
	sliderA.Step = 10
	delayLabelA := widget.NewLabel(fmt.Sprintf("Затримка A: %d мс", int(sliderA.Value)))
	sliderA.OnChanged = func(v float64) {
		atomic.StoreInt32(&s.state.DelayMsA, int32(v))
		delayLabelA.SetText(fmt.Sprintf("Затримка A: %d мс", int(v)))
	}
	s.sliderA = sliderA
	s.delayLabelA = delayLabelA

	sliderB := widget.NewSlider(0, 500)
	sliderB.SetValue(float64(atomic.LoadInt32(&s.state.DelayMsB)))
	sliderB.Step = 10
	delayLabelB := widget.NewLabel(fmt.Sprintf("Затримка B: %d мс", int(sliderB.Value)))
	sliderB.OnChanged = func(v float64) {
		atomic.StoreInt32(&s.state.DelayMsB, int32(v))
		delayLabelB.SetText(fmt.Sprintf("Затримка B: %d мс", int(v)))
	}
	s.sliderB = sliderB
	s.delayLabelB = delayLabelB

	const sliderWrap = 300
	sliderRowA := container.NewGridWrap(fyne.NewSize(sliderWrap, 36), sliderA)
	sliderRowB := container.NewGridWrap(fyne.NewSize(sliderWrap, 36), sliderB)

	controls := container.NewVBox(
		widget.NewLabelWithStyle("Керування", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}),
		container.NewHBox(widget.NewLabel("Номінал розміну:"), denomEntry),
		requestBtn,
		insertBtn,
		autoCheck,
		delayLabelA,
		sliderRowA,
		delayLabelB,
		sliderRowB,
	)
	controlsPanel := container.NewHBox(controls, layout.NewSpacer())

	// --- Event log ---
	logText := widget.NewMultiLineEntry()
	logText.Wrapping = fyne.TextWrapWord
	logText.SetMinRowsVisible(12)
	logText.Disable()
	s.logBind.AddListener(binding.NewDataListener(func() {
		txt, _ := s.logBind.Get()
		logText.SetText(txt)
		logText.CursorRow = strings.Count(txt, "\n")
		logText.Refresh()
	}))

	logPanel := container.NewBorder(
		widget.NewLabelWithStyle("Лог подій", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}),
		nil, nil, nil,
		container.NewScroll(logText),
	)

	topSplit := container.NewHSplit(
		container.NewHBox(bankBox, liveBox),
		dekkerBox,
	)
	topSplit.SetOffset(0.42)

	status := widget.NewLabelWithData(s.statusBinding)

	return container.NewBorder(
		topSplit, status, controlsPanel, nil,
		logPanel,
	)
}

func (s *supervisor) shutdown() {
	if s.state != nil {
		atomic.StoreInt32(&s.state.Stop, 1)
	}
	deadline := time.Now().Add(2 * time.Second)
	for _, c := range []*exec.Cmd{s.procA, s.procB} {
		if c == nil || c.Process == nil {
			continue
		}
		done := make(chan struct{})
		go func() { c.Wait(); close(done) }()
		select {
		case <-done:
		case <-time.After(time.Until(deadline)):
			_ = c.Process.Signal(syscall.SIGTERM)
		}
	}
	if s.seg != nil {
		s.seg.Detach()
		s.seg.Remove()
		s.seg = nil
	}
}
