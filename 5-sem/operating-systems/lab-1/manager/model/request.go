package model

import (
	"bytes"
	"encoding/gob"
	"time"
)

/* Request is the base request type
* Code 0 is success/Data request
* Code 1 is non-fatal error
* Code 2 is fatal error
* Code 3 is computation cancelling request
* Code 4 is status request
 */

const (
	SuccessCode       uint8 = iota
	NonFatalErrorCode uint8 = iota
	FatalErrorCode    uint8 = iota
	CancelRequestCode uint8 = iota
	StatusRequestCode uint8 = iota
)

type Request struct {
	Time int64
	Code uint8
}

func (r *Request) IsDataRequest() bool {
	return r.Code == SuccessCode
}

func (r *Request) IsCancelRequest() bool {
	return r.Code == CancelRequestCode
}

func (r *Request) IsStatusRequest() bool {
	return r.Code == StatusRequestCode
}

func (r *Request) GetTime() (time.Time, error) {
	return time.Unix(0, r.Time), nil
}

func NewCancelRequest() *Request {
	return &Request{
		Time: time.Now().UnixNano(),
		Code: CancelRequestCode,
	}
}

func (r *Request) Serialize() ([]byte, error) {
	var buffer bytes.Buffer
	encoder := gob.NewEncoder(&buffer)
	e := encoder.Encode(r)
	if e != nil {
		return nil, e
	}
	return buffer.Bytes(), nil
}

func DeserializeRequest(data []byte) (*Request, error) {
	var buffer bytes.Buffer
	_, e := buffer.Write(data)
	if e != nil {
		return nil, e
	}
	decoder := gob.NewDecoder(&buffer)
	var request Request
	e = decoder.Decode(&request)
	if e != nil {
		return nil, e
	}
	return &request, nil
}

type RequestData struct {
	Request
	ContentType string
	DataSize    int32
	Data        []byte
}

type Serializable interface {
	Serialize() ([]byte, error)
}

func NewDataRequest(contentType string, data []byte) *RequestData {
	return &RequestData{
		Request{
			Time: time.Now().UnixNano(),
			Code: SuccessCode,
		},
		contentType,
		int32(len(data)),
		data,
	}
}

func NewStatusRequestData(status []byte) *RequestData {
	return &RequestData{
		Request{
			Time: time.Now().UnixNano(),
			Code: StatusRequestCode,
		},
		"raw/status",
		int32(len(status)),
		status,
	}
}

func (r *RequestData) Serialize() ([]byte, error) {
	var buffer bytes.Buffer
	encoder := gob.NewEncoder(&buffer)
	e := encoder.Encode(r)
	if e != nil {
		return nil, e
	}
	return buffer.Bytes(), nil
}

func DeserializeRequestData(data []byte) (*RequestData, error) {
	var buffer bytes.Buffer
	_, e := buffer.Write(data)
	if e != nil {
		return nil, e
	}
	decoder := gob.NewDecoder(&buffer)
	var request RequestData
	e = decoder.Decode(&request)
	if e != nil {
		return nil, e
	}
	return &request, nil
}