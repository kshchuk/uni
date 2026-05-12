// Command process_a models the coin-acceptance side of the change machine.
// It attaches to a System V shared memory segment whose id is passed in
// the LAB3_SHM_ID environment variable, then runs an infinite loop that:
//
//   1. Waits for an "insert coin" trigger.  Two sources are accepted —
//      the auto-mode flag in shared state (used for stress tests) or a
//      one-shot command flag set by the supervisor in response to a GUI
//      click.
//   2. Identifies the denomination of the coin via a pseudorandom draw
//      over {1, 2, 5, 10, 25, 50, 100} kopiykas.
//   3. Enters the critical section via Dekker's algorithm and writes the
//      coin into the shared mailbox; if the coin belongs to the change
//      pool denominations, it is also added to the bank counter so it
//      can be used as change for subsequent customers.
//   4. Leaves the critical section and sleeps for DelayMsA milliseconds.
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
		ipc.Stderrf("process_a: LAB3_SHM_ID env var missing or invalid: %q", idStr)
		os.Exit(2)
	}
	seg, err := shm.Attach(id)
	if err != nil {
		ipc.Stderrf("process_a: shm.Attach(%d): %v", id, err)
		os.Exit(2)
	}
	defer seg.Detach()

	out := ipc.NewWriter(os.Stdout)
	out.Emit(ipc.Event{Process: "A", Kind: ipc.KindStart, Mode: dekker.Mode})

	state := seg.State
	view := shm.DekkerView(state)
	rng := rand.New(rand.NewSource(time.Now().UnixNano()))

	for atomic.LoadInt32(&state.Stop) == 0 {
		if !shouldInsert(state) {
			time.Sleep(5 * time.Millisecond)
			continue
		}

		coin := shm.Denominations[rng.Intn(len(shm.Denominations))]

		dekker.Enter(view, dekker.ProcA)
		recordCSEnter(state)

		atomic.StoreInt32(&state.MboxCoin, coin)
		atomic.StoreInt32(&state.MboxFull, 1)
		atomic.StoreInt32(&state.MboxResult, 0)
		atomic.StoreInt32(&state.MboxRefuseCode, 0)
		coinbank.AddIncoming((*[6]int32)(&state.Bank), coin)
		atomic.StoreInt32(&state.LastA, coin)
		atomic.AddInt64(&state.EnterA, 1)

		out.Emit(ipc.Event{
			Process: "A",
			Kind:    ipc.KindEnterCS,
			Coin:    coin,
		})
		out.Emit(ipc.Event{
			Process: "A",
			Kind:    ipc.KindDeposit,
			Coin:    coin,
		})

		recordCSLeave(state)
		dekker.Leave(view, dekker.ProcA)
		out.Emit(ipc.Event{Process: "A", Kind: ipc.KindLeaveCS, Coin: coin})

		sleepFor(atomic.LoadInt32(&state.DelayMsA))
	}

	out.Emit(ipc.Event{Process: "A", Kind: ipc.KindStop})
}

// shouldInsert returns true if the worker is allowed to take a coin in
// this iteration: either auto-mode is on, or a one-shot CmdInsert was
// raised by the supervisor (which we then consume atomically).
func shouldInsert(s *shm.State) bool {
	if atomic.LoadInt32(&s.AutoMode) == 1 {
		return true
	}
	return atomic.CompareAndSwapInt32(&s.CmdInsert, 1, 0)
}

func sleepFor(ms int32) {
	if ms <= 0 {
		ms = 50
	}
	time.Sleep(time.Duration(ms) * time.Millisecond)
}

// recordCSEnter increments the shared in-CS counter and updates the
// running maximum.  When mutual exclusion is broken this counter exceeds
// 1, which the supervisor reports as a collision.
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
