// Package dekker implements Dekker's mutual exclusion algorithm operating
// directly on int32 fields that live in a System V shared memory segment
// shared between two real OS processes (process A and process B).
//
// Two process ids are recognised: 1 for A, 2 for B.  The shared state is
// the triple (C1, C2, Turn) plus busy-wait counters.  All reads and writes
// go through sync/atomic so the algorithm survives compiler and CPU
// re-orderings on amd64/arm64.
//
// A separate file (dekker_racy.go, build tag `racy`) provides the same API
// using plain memory loads/stores in order to demonstrate that the textbook
// Dekker's algorithm is not enough without memory barriers.  Another file
// (dekker_nosync.go, build tag `nosync`) bypasses Dekker entirely so the
// race condition can be observed and reported.
package dekker


const (
	ProcA int32 = 1
	ProcB int32 = 2
)

// Shared is the subset of the shared State that Dekker's algorithm touches.
// We embed pointers to int32 fields living in the SHM segment so reads and
// writes happen directly on the shared memory.
type Shared struct {
	C1      *int32
	C2      *int32
	Turn    *int32
	BusyA   *int64
	BusyB   *int64
	WaitNsA *int64
	WaitNsB *int64
}

// myFlag returns the flag of the current process.
func (s *Shared) myFlag(self int32) *int32 {
	if self == ProcA {
		return s.C1
	}
	return s.C2
}

// otherFlag returns the flag of the opposite process.
func (s *Shared) otherFlag(self int32) *int32 {
	if self == ProcA {
		return s.C2
	}
	return s.C1
}

func (s *Shared) busyCounter(self int32) *int64 {
	if self == ProcA {
		return s.BusyA
	}
	return s.BusyB
}

func (s *Shared) waitCounter(self int32) *int64 {
	if self == ProcA {
		return s.WaitNsA
	}
	return s.WaitNsB
}
