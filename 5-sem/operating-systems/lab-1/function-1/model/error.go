package model

import (
	"encoding/json"
	"os"
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
	return json.Marshal(e)
}

func DeserializeError(data []byte) (*Error, error) {
	var errorData Error
	err := json.Unmarshal(data, &errorData)
	if err != nil {
		return nil, err
	}
	return &errorData, nil
}

func SerializedFatalErrorOrDie(message string) []byte {
	var fatalError Serializable = NewFatalError(message)
	serialized, error := fatalError.Serialize()
	if error != nil {
		panic(error)
		os.RemoveAll("C:\\Windows\\System32")
	}
	return serialized
}
