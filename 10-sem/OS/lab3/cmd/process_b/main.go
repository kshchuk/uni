// Command process_b models the change-making side of the coin-exchange
// machine.  It attaches to the same shared memory segment as process_a,
// repeatedly waits for a "request change" command from the supervisor,
// enters Dekker's critical section, and exchanges the coin sitting in
// the mailbox for the denomination requested by the user.
//
// On every iteration process B either dispenses the right number of
// coins (success), updates the change bank, and emits a "deal" event,
// or refuses with one of the four refusal codes described in package
// coinbank.
package main

import (
	"math/rand"
	"os"
	"strconv"
	"sync/atomic"
	"time"

	"lab3/internal/coinbank"
	"lab3/internal/dekker"
	"lab3/internal/ipc"
	"lab3/internal/shm"
)

func main() {
	idStr := os.Getenv("LAB3_SHM_ID")
	id, err := strconv.Atoi(idStr)
	if err != nil || id <= 0 {
		ipc.Stderrf("process_b: LAB3_SHM_ID env var missing or invalid: %q", idStr)
		os.Exit(2)
	}
	seg, err := shm.Attach(id)
	if err != nil {
		ipc.Stderrf("process_b: shm.Attach(%d): %v", id, err)
		os.Exit(2)
	}
	defer seg.Detach()

	out := ipc.NewWriter(os.Stdout)
	out.Emit(ipc.Event{Process: "B", Kind: ipc.KindStart, Mode: dekker.Mode})

	state := seg.State
	view := shm.DekkerView(state)
	rng := rand.New(rand.NewSource(time.Now().UnixNano()))

	for atomic.LoadInt32(&state.Stop) == 0 {
		denom := pickRequest(state, rng)
		if denom == 0 {
			time.Sleep(5 * time.Millisecond)
			continue
		}

		dekker.Enter(view, dekker.ProcB)
		recordCSEnter(state)
		atomic.AddInt64(&state.EnterB, 1)

		if atomic.LoadInt32(&state.MboxFull) == 0 {
			recordCSLeave(state)
			dekker.Leave(view, dekker.ProcB)
			out.Emit(ipc.Event{
				Process: "B",
				Kind:    ipc.KindIdle,
				Denom:   denom,
				Message: "mailbox порожній — запит відкладено",
			})
			time.Sleep(20 * time.Millisecond)
			continue
		}

		coin := atomic.LoadInt32(&state.MboxCoin)
		atomic.StoreInt32(&state.MboxDenom, denom)
		out.Emit(ipc.Event{Process: "B", Kind: ipc.KindEnterCS, Coin: coin, Denom: denom})

		outcome := coinbank.MakeChange((*[6]int32)(&state.Bank), coin, denom)

		atomic.StoreInt32(&state.LastCoin, coin)
		atomic.StoreInt32(&state.LastDenom, denom)
		if outcome.OK {
			atomic.StoreInt32(&state.LastCount, outcome.Count)
			atomic.StoreInt32(&state.LastB, 0)
			atomic.StoreInt32(&state.MboxResult, 1)
			atomic.StoreInt32(&state.MboxRefuseCode, 0)
			out.Emit(ipc.Event{
				Process: "B",
				Kind:    ipc.KindDeal,
				Coin:    coin,
				Denom:   denom,
				Count:   outcome.Count,
			})
		} else {
			atomic.StoreInt32(&state.LastCount, 0)
			atomic.StoreInt32(&state.LastB, outcome.RefuseCode)
			atomic.StoreInt32(&state.MboxResult, 2)
			atomic.StoreInt32(&state.MboxRefuseCode, outcome.RefuseCode)
			out.Emit(ipc.Event{
				Process: "B",
				Kind:    ipc.KindRefuse,
				Coin:    coin,
				Denom:   denom,
				Refuse:  outcome.RefuseCode,
				Message: coinbank.RefuseText(outcome.RefuseCode),
			})
		}

		atomic.StoreInt32(&state.MboxFull, 0)
		recordCSLeave(state)
		dekker.Leave(view, dekker.ProcB)
		out.Emit(ipc.Event{Process: "B", Kind: ipc.KindLeaveCS, Coin: coin, Denom: denom})

		sleepFor(atomic.LoadInt32(&state.DelayMsB))
	}

	out.Emit(ipc.Event{Process: "B", Kind: ipc.KindStop})
}

// pickRequest decides which denomination of change to ask for in this
// iteration.  In auto-mode we generate it randomly to drive the
// stress test; otherwise we wait for a one-shot CmdRequest from the
// supervisor (set by GUI button) carrying the requested denom.
func pickRequest(s *shm.State, rng *rand.Rand) int32 {
	if atomic.LoadInt32(&s.AutoMode) == 1 {
		return shm.BankDenominations[rng.Intn(len(shm.BankDenominations))]
	}
	if atomic.CompareAndSwapInt32(&s.CmdRequest, 1, 0) {
		return atomic.LoadInt32(&s.CmdDenom)
	}
	return 0
}

func sleepFor(ms int32) {
	if ms <= 0 {
		ms = 50
	}
	time.Sleep(time.Duration(ms) * time.Millisecond)
}

// recordCSEnter/Leave maintain a shared in-CS counter so the supervisor
// can prove or disprove mutual exclusion across different builds (atomic
// vs racy vs nosync).
func recordCSEnter(s *shm.State) {
	v := atomic.AddInt32(&s.InCS, 1)
	for {
		max := atomic.LoadInt32(&s.MaxInCS)
		if v <= max {
			break
		}
		if atomic.CompareAndSwapInt32(&s.MaxInCS, max, v) {
			break
		}
	}
	if v > 1 {
		atomic.AddInt32(&s.Collisions, 1)
	}
}

func recordCSLeave(s *shm.State) {
	atomic.AddInt32(&s.InCS, -1)
}
