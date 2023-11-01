package model

import (
	"bytes"
	"encoding/gob"
	"time"
)

type FunctionControllerStatus struct {
	CriticalLimit    time.Duration
	NonCriticalLimit time.Duration
	ExecutionTime    time.Duration
	Status           string
}

func DeserializeFunctionControllerStatus(data []byte) (*FunctionControllerStatus, error) {
	var status FunctionControllerStatus
	dec := gob.NewDecoder(bytes.NewReader(data))
	err := dec.Decode(&status)
	if err != nil {
		return nil, err
	}
	return &status, nil
}

func (status *FunctionControllerStatus) String() string {
	return "FunctionControllerStatus{CriticalLimit: " + status.CriticalLimit.String() + ", NonCriticalLimit: " + status.NonCriticalLimit.String() + ", ExecutionTime: " + status.ExecutionTime.String() + ", Status: " + status.Status + "}"
}
