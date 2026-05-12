// Package ipc defines a tiny line-oriented JSON protocol used by the
// supervisor to receive log events from the worker processes.
//
// Each event is emitted as one JSON object terminated by '\n', written to
// the worker's stdout.  The supervisor reads stdout pipe-by-line and
// renders the messages in the log panel of the GUI.
package ipc

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"time"
)

// Kind enumerates the possible event types.  We use short string codes
// so the protocol stays readable in raw form (which is helpful when
// debugging or replaying logs offline).
type Kind string

const (
	KindStart    Kind = "start"
	KindStop     Kind = "stop"
	KindEnterCS  Kind = "enter_cs"
	KindLeaveCS  Kind = "leave_cs"
	KindDeposit  Kind = "deposit"
	KindDeal     Kind = "deal"
	KindRefuse   Kind = "refuse"
	KindIdle     Kind = "idle"
	KindInfo     Kind = "info"
	KindWarn     Kind = "warn"
)

// Event is the JSON payload exchanged via stdout.  Fields with zero values
// are omitted so the log stays compact.
type Event struct {
	TS       int64  `json:"ts"`              // unix nano
	Process  string `json:"proc"`            // "A" or "B"
	Kind     Kind   `json:"kind"`
	Coin     int32  `json:"coin,omitempty"`
	Denom    int32  `json:"denom,omitempty"`
	Count    int32  `json:"count,omitempty"`
	Refuse   int32  `json:"refuse,omitempty"`
	Mode     string `json:"mode,omitempty"`
	Message  string `json:"msg,omitempty"`
}

// Writer wraps an io.Writer and emits one JSON event per line.  Writes are
// buffered behind an explicit Flush so we can drain after each event.
type Writer struct {
	w   *bufio.Writer
	buf []byte
}

func NewWriter(w io.Writer) *Writer { return &Writer{w: bufio.NewWriter(w)} }

func (w *Writer) Emit(e Event) {
	if e.TS == 0 {
		e.TS = time.Now().UnixNano()
	}
	b, err := json.Marshal(e)
	if err != nil {
		return
	}
	w.buf = append(w.buf[:0], b...)
	w.buf = append(w.buf, '\n')
	_, _ = w.w.Write(w.buf)
	_ = w.w.Flush()
}

// Stderrf is a convenience helper used by worker processes to write a
// fatal error to stderr so that the supervisor can surface it.
func Stderrf(format string, args ...any) {
	fmt.Fprintf(os.Stderr, format+"\n", args...)
}

// Reader wraps a bufio.Scanner and returns parsed events one by one.
type Reader struct {
	sc *bufio.Scanner
}

func NewReader(r io.Reader) *Reader {
	sc := bufio.NewScanner(r)
	sc.Buffer(make([]byte, 64*1024), 1024*1024)
	return &Reader{sc: sc}
}

// Next reads one event.  On EOF returns io.EOF.
func (r *Reader) Next() (Event, error) {
	if !r.sc.Scan() {
		if err := r.sc.Err(); err != nil {
			return Event{}, err
		}
		return Event{}, io.EOF
	}
	var ev Event
	if err := json.Unmarshal(r.sc.Bytes(), &ev); err != nil {
		return Event{}, err
	}
	return ev, nil
}
