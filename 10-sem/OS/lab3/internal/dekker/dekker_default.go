//go:build !racy && !nosync

package dekker

// Mode is reported by the binary on startup so the operator knows which
// implementation is in use.  See the racy/nosync build tags for the
// alternatives.
const Mode = "dekker-atomic"

// Enter implements the entry protocol of Dekker's algorithm for two
// processes.  self must be ProcA or ProcB.
//
// The structure mirrors the pseudocode from the lab handout (section
// "Алгоритм Деккера"):
//
//	C[self] := 1
//	while C[other] = 1:
//	    if Turn = other:
//	        C[self] := 0
//	        while Turn = other: spin
//	        C[self] := 1
//
// All accesses to C1/C2/Turn are performed with sync/atomic primitives.
// On amd64 the underlying machine instructions are already sequentially
// consistent for aligned int32 operations, while on arm64 the atomic
// intrinsics emit dmb/ldar/stlr fences as required.
func Enter(s *Shared, self int32) {
	other := otherID(self)
	start := nowNs()

	storeInt32(s.myFlag(self), 1)

	for loadInt32(s.otherFlag(self)) == 1 {
		if loadInt32(s.Turn) == other {
			storeInt32(s.myFlag(self), 0)
			for loadInt32(s.Turn) == other {
				addInt64(s.busyCounter(self), 1)
				yieldCPU()
			}
			storeInt32(s.myFlag(self), 1)
		} else {
			addInt64(s.busyCounter(self), 1)
			yieldCPU()
		}
	}

	addInt64(s.waitCounter(self), nowNs()-start)
}

// Leave implements the exit protocol: yield the turn to the peer and clear
// the local intent flag.
func Leave(s *Shared, self int32) {
	storeInt32(s.Turn, otherID(self))
	storeInt32(s.myFlag(self), 0)
}
