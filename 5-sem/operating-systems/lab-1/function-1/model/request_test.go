package model

import (
	"bytes"
	"testing"
	"time"
)

func TestRequest(t *testing.T) {
	req := &Request{
		Time: time.Now().UnixNano(),
		Code: SuccessCode,
	}

	if !req.IsSuccess() {
		t.Errorf("Expected request to be success")
	}

	if req.IsCancelRequest() {
		t.Errorf("Expected request not to be cancel request")
	}

	if req.IsStatusRequest() {
		t.Errorf("Expected request not to be status request")
	}
}

func TestRequestData(t *testing.T) {
	data := []byte("Hello, World!")
	reqData := NewDataRequest("text/plain", data)

	if reqData.ContentType != "text/plain" {
		t.Errorf("Expected content type to be 'text/plain'")
	}

	if reqData.DataSize != int32(len(data)) {
		t.Errorf("Expected data size to be %d", len(data))
	}

	if bytes.Compare(reqData.Data, data) != 0 {
		t.Errorf("Expected data to be '%s'", data)
	}

	serialized, e := reqData.Serialize()
	if e != nil {
		t.Errorf("Unexpected error: %v", e)
	}
	deserialized, e := DeserializeRequestData(serialized)
	if e != nil {
		t.Errorf("Unexpected error: %v", e)
	}

	if bytes.Compare(deserialized.Data, data) != 0 {
		t.Errorf("Expected deserialized data to be '%s'", data)
	}
}
