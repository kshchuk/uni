// poke is a tiny CLI helper that attaches to an existing SHM segment
// (id is taken from --id or from `ipcs -m`) and lets the operator flip
// control flags or push commands.  It is useful for scripting GUI
// scenarios when capturing screenshots/recordings.
//
// Usage:
//
//	go run ./examples/poke --id 65536 --auto on
//	go run ./examples/poke --id 65536 --insert
//	go run ./examples/poke --id 65536 --request 2
//	go run ./examples/poke --id 65536 --print
package main

import (
	"flag"
	"fmt"
	"log"
	"os/exec"
	"strconv"
	"strings"
	"sync/atomic"

	"lab3/internal/shm"
)

func main() {
	id := flag.Int("id", 0, "SHM id; 0 means auto-detect via ipcs -m")
	auto := flag.String("auto", "", "set auto-mode: on/off")
	insert := flag.Bool("insert", false, "trigger one coin insertion (A)")
	request := flag.Int("request", 0, "trigger one change request for the given denomination (B)")
	delayA := flag.Int("delay-a", -1, "set DelayMsA")
	delayB := flag.Int("delay-b", -1, "set DelayMsB")
	print := flag.Bool("print", false, "print current state and exit")
	flag.Parse()

	if *id == 0 {
		v, err := detectSHM()
		if err != nil {
			log.Fatalf("detect SHM: %v", err)
		}
		*id = v
	}
	seg, err := shm.Attach(*id)
	if err != nil {
		log.Fatalf("attach %d: %v", *id, err)
	}
	defer seg.Detach()
	st := seg.State

	switch strings.ToLower(*auto) {
	case "on":
		atomic.StoreInt32(&st.AutoMode, 1)
	case "off":
		atomic.StoreInt32(&st.AutoMode, 0)
	}
	if *insert {
		atomic.StoreInt32(&st.CmdInsert, 1)
	}
	if *request > 0 {
		atomic.StoreInt32(&st.CmdDenom, int32(*request))
		atomic.StoreInt32(&st.CmdRequest, 1)
	}
	if *delayA >= 0 {
		atomic.StoreInt32(&st.DelayMsA, int32(*delayA))
	}
	if *delayB >= 0 {
		atomic.StoreInt32(&st.DelayMsB, int32(*delayB))
	}

	if *print {
		fmt.Printf("SHM id=%d\n", *id)
		fmt.Printf("  C1=%d C2=%d Turn=%d\n", st.C1, st.C2, st.Turn)
		fmt.Printf("  EnterA=%d EnterB=%d  BusyA=%d BusyB=%d\n", st.EnterA, st.EnterB, st.BusyA, st.BusyB)
		fmt.Printf("  Collisions=%d  MaxInCS=%d\n", st.Collisions, st.MaxInCS)
		fmt.Printf("  AutoMode=%d  DelayMsA=%d DelayMsB=%d\n", st.AutoMode, st.DelayMsA, st.DelayMsB)
		fmt.Printf("  Bank: ")
		for i, d := range shm.BankDenominations {
			fmt.Printf("%dk=%d ", d, st.Bank[i])
		}
		fmt.Println()
	}
}

// detectSHM finds the most recent SHM segment owned by the current user.
func detectSHM() (int, error) {
	out, err := exec.Command("ipcs", "-m").Output()
	if err != nil {
		return 0, err
	}
	var id int
	for _, line := range strings.Split(string(out), "\n") {
		f := strings.Fields(line)
		if len(f) >= 2 && f[0] == "m" {
			n, err := strconv.Atoi(f[1])
			if err == nil {
				id = n
			}
		}
	}
	if id == 0 {
		return 0, fmt.Errorf("no SHM segment found via ipcs -m")
	}
	return id, nil
}
