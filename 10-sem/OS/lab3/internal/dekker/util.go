package dekker

import (
	"runtime"
	"sync/atomic"
	"time"
	"unsafe"
)

func otherID(self int32) int32 {
	if self == ProcA {
		return ProcB
	}
	return ProcA
}

func nowNs() int64 { return time.Now().UnixNano() }

func yieldCPU() { runtime.Gosched() }

// --- atomic primitives, used by the default implementation ---

func loadInt32(p *int32) int32   { return atomic.LoadInt32(p) }
func storeInt32(p *int32, v int32) { atomic.StoreInt32(p, v) }
func addInt64(p *int64, v int64)   { atomic.AddInt64(p, v) }

// --- plain (racy) primitives, used by the `racy` build ---

// loadInt32Raw reads through unsafe.Pointer to defeat any optimisation
// that might cache the value in a register.  Even so, this DOES NOT
// emit a memory barrier and therefore can return stale values on
// re-ordering architectures.
func loadInt32Raw(p *int32) int32 {
	return *(*int32)(unsafe.Pointer(p))
}

func storeInt32Raw(p *int32, v int32) {
	*(*int32)(unsafe.Pointer(p)) = v
}

// addInt64Raw is not strictly racy because it is only used for metrics
// counters that we do not depend on for correctness; we still use atomic
// here so the numbers shown to the user are well defined.
func addInt64Raw(p *int64, v int64) {
	atomic.AddInt64(p, v)
}
