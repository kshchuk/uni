// smoketest spawns process_a and process_b in auto-mode for a few seconds
// and prints the resulting metrics.  It is intended as a quick sanity
// check that Dekker's algorithm allows progress without the GUI.
//
// Usage:
//
//	go run ./examples/smoketest --duration 3s
package main

import (
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"sync/atomic"
	"time"

	"lab3/internal/ipc"
	"lab3/internal/shm"
)

func main() {
	duration := flag.Duration("duration", 3*time.Second, "how long to run the workers")
	autoB := flag.Bool("auto_b", true, "let process_b also run in auto mode")
	flag.Parse()

	seg, err := shm.Create()
	if err != nil {
		log.Fatalf("create SHM: %v", err)
	}
	defer func() {
		seg.Detach()
		seg.Remove()
	}()
	st := seg.State

	for i, v := range [6]int32{200, 200, 200, 200, 200, 200} {
		atomic.StoreInt32(&st.Bank[i], v)
	}
	atomic.StoreInt32(&st.Turn, 1)
	atomic.StoreInt32(&st.DelayMsA, 5)
	atomic.StoreInt32(&st.DelayMsB, 5)
	atomic.StoreInt32(&st.AutoMode, 1)
	_ = autoB

	root := mustRoot()
	procA := exec.Command(filepath.Join(root, "bin", "process_a"))
	procB := exec.Command(filepath.Join(root, "bin", "process_b"))
	for _, c := range []*exec.Cmd{procA, procB} {
		c.Env = append(os.Environ(), "LAB3_SHM_ID="+strconv.Itoa(seg.ID))
		c.Stderr = os.Stderr
	}
	pa, _ := procA.StdoutPipe()
	pb, _ := procB.StdoutPipe()
	if err := procA.Start(); err != nil {
		log.Fatalf("start A: %v", err)
	}
	if err := procB.Start(); err != nil {
		log.Fatalf("start B: %v", err)
	}

	cntA := countEvents(pa)
	cntB := countEvents(pb)

	time.Sleep(*duration)

	atomic.StoreInt32(&st.Stop, 1)
	procA.Wait()
	procB.Wait()

	fmt.Printf("== Metrics after %v ==\n", *duration)
	fmt.Printf("  EnterA=%d EnterB=%d\n", atomic.LoadInt64(&st.EnterA), atomic.LoadInt64(&st.EnterB))
	fmt.Printf("  BusyA=%d  BusyB=%d\n", atomic.LoadInt64(&st.BusyA), atomic.LoadInt64(&st.BusyB))
	fmt.Printf("  Wait msA=%.2f msB=%.2f\n", float64(atomic.LoadInt64(&st.WaitNsA))/1e6, float64(atomic.LoadInt64(&st.WaitNsB))/1e6)
	fmt.Printf("  events A=%d events B=%d\n", <-cntA, <-cntB)
	fmt.Printf("  CS collisions=%d max-in-CS=%d\n", atomic.LoadInt32(&st.Collisions), atomic.LoadInt32(&st.MaxInCS))
	fmt.Printf("  bank: ")
	for i, d := range shm.BankDenominations {
		fmt.Printf("%dk=%d ", d, atomic.LoadInt32(&st.Bank[i]))
	}
	fmt.Println()
}

func mustRoot() string {
	wd, err := os.Getwd()
	if err != nil {
		log.Fatal(err)
	}
	return wd
}

// countEvents consumes the worker's stdout and returns the count via a
// channel after EOF.
func countEvents(r io.Reader) <-chan int {
	out := make(chan int, 1)
	go func() {
		reader := ipc.NewReader(r)
		n := 0
		for {
			_, err := reader.Next()
			if err != nil {
				out <- n
				return
			}
			n++
		}
	}()
	return out
}
