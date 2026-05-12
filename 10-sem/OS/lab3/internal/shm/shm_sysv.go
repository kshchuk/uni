//go:build darwin || linux

// Package shm provides a thin cgo wrapper around the System V shared memory
// API (shmget/shmat/shmdt/shmctl) so that two unrelated processes can share
// a fixed-size State structure.
//
// We use IPC_PRIVATE keys: the supervisor creates the segment, prints the
// resulting numeric id, sets it into the LAB3_SHM_ID environment variable
// for the children, and removes the segment with IPC_RMID on exit.
package shm

/*
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <errno.h>
#include <string.h>

// shm_create wraps shmget(IPC_PRIVATE, size, IPC_CREAT|IPC_EXCL|0600).
static int shm_create(size_t size, int *err) {
    int id = shmget(IPC_PRIVATE, size, IPC_CREAT | IPC_EXCL | 0600);
    if (id < 0) {
        *err = errno;
    }
    return id;
}

// shm_attach maps an existing segment into the address space.
static void *shm_attach(int id, int *err) {
    void *p = shmat(id, NULL, 0);
    if (p == (void *)-1) {
        *err = errno;
        return NULL;
    }
    return p;
}

static int shm_detach(void *p) {
    if (shmdt(p) < 0) {
        return errno;
    }
    return 0;
}

static int shm_remove(int id) {
    if (shmctl(id, IPC_RMID, NULL) < 0) {
        return errno;
    }
    return 0;
}
*/
import "C"

import (
	"fmt"
	"unsafe"
)

// Segment owns a handle to a System V shared memory segment together with
// a pointer to its mapped State.
type Segment struct {
	ID    int
	State *State
	addr  unsafe.Pointer
}

// stateSize is the byte size of State as understood by C.
func stateSize() C.size_t {
	return C.size_t(unsafe.Sizeof(State{}))
}

// Create allocates and attaches a new private segment large enough to hold
// a State.  The caller is responsible for calling Remove when the segment
// is no longer needed (typically the supervisor on shutdown).
func Create() (*Segment, error) {
	var cerr C.int
	id := C.shm_create(stateSize(), &cerr)
	if id < 0 {
		return nil, fmt.Errorf("shmget: errno=%d (%s)", int(cerr), errnoMessage(int(cerr)))
	}
	seg, err := attach(int(id))
	if err != nil {
		// Best-effort cleanup: an unattached segment would be leaked.
		C.shm_remove(id)
		return nil, err
	}
	// Zero the segment so that fields start from known values.
	*seg.State = State{}
	return seg, nil
}

// Attach opens an existing segment identified by the supervisor.
func Attach(id int) (*Segment, error) {
	return attach(id)
}

func attach(id int) (*Segment, error) {
	var cerr C.int
	addr := C.shm_attach(C.int(id), &cerr)
	if addr == nil {
		return nil, fmt.Errorf("shmat: errno=%d (%s)", int(cerr), errnoMessage(int(cerr)))
	}
	st := (*State)(addr)
	return &Segment{ID: id, State: st, addr: unsafe.Pointer(addr)}, nil
}

// Detach unmaps the segment from this process.  It does NOT free the
// underlying segment; only Remove does that.
func (s *Segment) Detach() error {
	if s == nil || s.addr == nil {
		return nil
	}
	rc := C.shm_detach(s.addr)
	s.addr = nil
	s.State = nil
	if rc != 0 {
		return fmt.Errorf("shmdt: errno=%d (%s)", int(rc), errnoMessage(int(rc)))
	}
	return nil
}

// Remove deletes the segment via IPC_RMID.  Once the last attached process
// detaches, the kernel reclaims the memory.
func (s *Segment) Remove() error {
	if s == nil {
		return nil
	}
	rc := C.shm_remove(C.int(s.ID))
	if rc != 0 {
		return fmt.Errorf("shmctl IPC_RMID: errno=%d (%s)", int(rc), errnoMessage(int(rc)))
	}
	return nil
}

func errnoMessage(e int) string {
	switch e {
	case 0:
		return "ok"
	case 1:
		return "EPERM"
	case 12:
		return "ENOMEM"
	case 13:
		return "EACCES"
	case 17:
		return "EEXIST"
	case 22:
		return "EINVAL"
	case 28:
		return "ENOSPC"
	default:
		return "errno"
	}
}
