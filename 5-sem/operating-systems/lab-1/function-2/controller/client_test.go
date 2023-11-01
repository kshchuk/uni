package controller

import (
	"lab-1/function-1/model"
	"lab-1/function-1/util"
	"net"
	"testing"
	"time"
)

func TestHandleRequest(t *testing.T) {
	conn, _ := net.Dial("tcp", "localhost:8080")
	client := NewClient(conn)

	// Test case for StatusRequest
	reqd := model.NewStatusRequestData([]byte("status"))
	data, _ := reqd.Serialize()
	resp := client.handleRequest(data)
	if resp == nil {
		t.Errorf("Expected status response, got nil")
	}

	// Test case for CancelRequest
	req := model.NewCancelRequest()
	data, _ = req.Serialize()
	resp = client.handleRequest(data)
	if resp != nil {
		t.Errorf("Expected nil response, got %v", resp)
	}

	// Test case for DataRequest
	reqData := model.NewDataRequest("int64", []byte("5"))
	data, _ = reqData.Serialize()
	resp = client.handleRequest(data)
	if resp == nil {
		t.Errorf("Expected data response, got nil")
	}

	// Test case for unknown request type
	req = &model.Request{Time: time.Now().UnixNano(), Code: 99}
	data, _ = req.Serialize()
	resp = client.handleRequest(data)
	if resp == nil {
		t.Errorf("Expected error response, got nil")
	}
}

func TestExecFunction(t *testing.T) {
	conn, _ := net.Dial("tcp", "localhost:8080")
	client := NewClient(conn)

	// Test case for execFunction with valid data
	argBytes, _ := util.ToBytes(int64(5))
	reqData := model.NewDataRequest("int64", argBytes)
	resp, err := client.execFunction(reqData)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if resp == nil {
		t.Errorf("Expected response, got nil")
	}
	// Check if response data is correct
	resps, errs := resp.Serialize()
	if errs != nil {
		t.Errorf("Expected no error, got %v", errs)
	}
	if resp == nil {
		t.Errorf("Expected response, got nil")
	}
	respData, errrrr := model.DeserializeRequestData(resps)
	if errrrr != nil {
		t.Errorf("Expected no error, got %v", errrrr)
	}
	if respData == nil {
		t.Errorf("Expected response data, got nil")
	}
	if respData.ContentType != "int64" {
		t.Errorf("Expected response data type int64, got %v", respData.ContentType)
	}
	res, errrr := util.FromBytes(respData.Data)
	if errrr != nil {
		t.Errorf("Expected no error, got %v", errrr)
	}
	if res != 120 {
		t.Errorf("Expected response data 120, got %v", res)
	}

	// Test case for execFunction with invalid data
	reqData = model.NewDataRequest("int64", []byte("invalid"))
	resp, err = client.execFunction(reqData)
	if err == nil {
		t.Errorf("Expected error, got nil")
	}
	if resp != nil {
		t.Errorf("Expected nil response, got %v", resp)
	}
}
