//go:build racy

package dekker

// Mode reports that we are running the demonstration version of Dekker's
// algorithm where the shared flags are read and written without any atomic
// or memory-barrier primitives.  On modern out-of-order CPUs the algorithm
// is known to break in this configuration: stores to one's own flag can be
// re-ordered after loads of the peer's flag, so both processes can decide
// to enter the critical section simultaneously.
const Mode = "dekker-racy"

func Enter(s *Shared, self int32) {
	other := otherID(self)
	start := nowNs()

	storeInt32Raw(s.myFlag(self), 1)

	for loadInt32Raw(s.otherFlag(self)) == 1 {
		if loadInt32Raw(s.Turn) == other {
			storeInt32Raw(s.myFlag(self), 0)
			for loadInt32Raw(s.Turn) == other {
				addInt64Raw(s.busyCounter(self), 1)
				yieldCPU()
			}
			storeInt32Raw(s.myFlag(self), 1)
		} else {
			addInt64Raw(s.busyCounter(self), 1)
			yieldCPU()
		}
	}

	addInt64Raw(s.waitCounter(self), nowNs()-start)
}

func Leave(s *Shared, self int32) {
	storeInt32Raw(s.Turn, otherID(self))
	storeInt32Raw(s.myFlag(self), 0)
}
