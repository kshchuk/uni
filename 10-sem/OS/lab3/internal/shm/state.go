package shm

// Coin denominations accepted by the machine (kopiykas; 100 == 1 hryvnia).
// Bank stores change pool only for the first 6 (kopiyka coins); 1 hryvnia
// coins are not used as change.
var Denominations = [7]int32{1, 2, 5, 10, 25, 50, 100}

// BankDenominations are the 6 denominations stored in the change bank
// (the 1 hryvnia coin is not dispensed as change).
var BankDenominations = [6]int32{1, 2, 5, 10, 25, 50}

// Refuse codes emitted by process B.
const (
	RefuseInvalidDenom    int32 = 1 // denomination is not in {1,2,5,10,25,50}
	RefuseDenomGEQCoin    int32 = 2 // denomination >= coin value
	RefuseIndivisible     int32 = 3 // coin % denom != 0
	RefuseInsufficientBox int32 = 4 // not enough coins of required denomination
)

// State is the shared structure placed into the System V shared memory
// segment.  Every field is fixed-size so that a process attaching to the
// segment can interpret the bytes identically regardless of compiler
// padding (we use only int32/int64 aligned to 8-byte boundaries).
type State struct {
	// --- Dekker's algorithm shared flags ---
	C1   int32 // process A wants to enter critical section
	C2   int32 // process B wants to enter critical section
	Turn int32 // whose turn it is (1 == A, 2 == B)

	_pad0 int32 // alignment

	// --- Mailbox: A delivers coin and B writes back result ---
	MboxFull       int32 // 0 == empty, 1 == coin sitting in the box
	MboxCoin       int32 // coin denomination deposited by A
	MboxDenom      int32 // denomination requested for change
	MboxResult     int32 // 0 == pending, 1 == success, 2 == refuse
	MboxRefuseCode int32 // refuse reason (1..4) when MboxResult == 2

	_pad1 int32

	// --- Change bank (counts per BankDenominations) ---
	Bank [6]int32

	_pad2 [2]int32

	// --- Metrics (atomic int64) ---
	EnterA  int64 // number of times A entered its critical section
	EnterB  int64
	BusyA   int64 // busy-wait iterations spent by A
	BusyB   int64
	WaitNsA int64 // accumulated waiting time, ns
	WaitNsB int64

	// --- Control flags driven by supervisor ---
	Stop     int32 // 1 => children must terminate gracefully
	DelayMsA int32 // artificial delay in process A loop
	DelayMsB int32 // artificial delay in process B loop
	AutoMode int32 // 1 => A generates coins on its own without GUI clicks

	// --- Inbound commands from the supervisor (one-shot flags) ---
	CmdInsert   int32 // A consumes this to inject a coin
	CmdRequest  int32 // B consumes this to perform a change-making attempt
	CmdDenom    int32 // denomination requested with the latest CmdRequest

	_pad3 int32

	// --- Snapshot of last action for the GUI (informational only) ---
	LastA       int32 // last coin deposited by A
	LastB       int32 // last refuse code or 0 on success
	LastCoin    int32 // coin that was changed in the latest deal
	LastDenom   int32 // denomination used to make change
	LastCount   int32 // number of coins issued

	// --- Mutual-exclusion violation detector ---
	// InCS is incremented when a process enters the critical section
	// and decremented on leave.  A correctly synchronised run keeps it
	// in {0, 1}.  Reaching 2 means both processes were inside the CS
	// at the same time — a direct proof of broken mutual exclusion.
	InCS         int32
	MaxInCS      int32
	Collisions   int32

	_pad4 int32
}
