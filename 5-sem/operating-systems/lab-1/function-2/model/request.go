package model

import (
	"encoding/json"
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
	return json.Marshal(r)
}

func DeserializeRequest(data []byte) (*Request, error) {
	var request Request
	err := json.Unmarshal(data, &request)
	if err != nil {
		return nil, err
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
	return json.Marshal(r)
}

func DeserializeRequestData(data []byte) (*RequestData, error) {
	var requestData RequestData
	err := json.Unmarshal(data, &requestData)
	if err != nil {
		return nil, err
	}
	return &requestData, nil
}
