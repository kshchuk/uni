package model

import (
	"bytes"
	"encoding/gob"
	"time"
)

/* Error is the base error type
 * Code 0 is success
 * Code 1 is non-fatal error
 * Code 2 is fatal error
 */

type Error struct {
	Request
	Message string
}

func (r *Request) IsNonFatalError() bool {
	return r.Code == NonFatalErrorCode
}

func (r *Request) IsFatalError() bool {
	return r.Code == FatalErrorCode
}

func NewFatalError(message string) *Error {
	return &Error{
		Request{
			Code: FatalErrorCode,
			Time: time.Now().UnixNano(),
		},
		message,
	}
}

func NewNonFatalError(message string) *Error {
	return &Error{
		Request{
			Code: NonFatalErrorCode,
			Time: time.Now().UnixNano(),
		},
		message,
	}
}

func (e *Error) ErrorString() string {
	return e.Message
}

func (e *Error) Serialize() ([]byte, error) {
	var buf bytes.Buffer
	enc := gob.NewEncoder(&buf)
	err := enc.Encode(e)
	if err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

func DeserializeError(data []byte) (*Error, error) {
	var e Error
	buf := bytes.NewBuffer(data)
	dec := gob.NewDecoder(buf)
	err := dec.Decode(&e)
	if err != nil {
		return nil, err
	}
	return &e, nil
}
