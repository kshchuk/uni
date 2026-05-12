//go:build nosync

package dekker

// Mode reports that we are running the no-synchronisation build: Enter and
// Leave do nothing, which lets us observe how two processes corrupt the
// shared bank if they collide inside the critical section.
const Mode = "dekker-nosync"

func Enter(s *Shared, self int32) {
	// Account the wait time as zero but still tick the busy counter once
	// per call so the GUI shows we visited the entry routine.
	addInt64Raw(s.busyCounter(self), 0)
}

func Leave(s *Shared, self int32) {
	_ = s
	_ = self
}
