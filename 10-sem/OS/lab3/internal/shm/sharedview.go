package shm

import "lab3/internal/dekker"

// DekkerView extracts the pointers to the shared Dekker variables and
// metric counters from a State.  The returned struct is reused by both
// workers and lives only on the stack.
func DekkerView(s *State) *dekker.Shared {
	return &dekker.Shared{
		C1:      &s.C1,
		C2:      &s.C2,
		Turn:    &s.Turn,
		BusyA:   &s.BusyA,
		BusyB:   &s.BusyB,
		WaitNsA: &s.WaitNsA,
		WaitNsB: &s.WaitNsB,
	}
}
