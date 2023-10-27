package controller

import (
	"bytes"
	"context"
	"encoding/gob"
	"fmt"
	"lab-1/function-1/config"
	"lab-1/function-1/model"
	"time"
)

type FunctionController struct {
	criticalLimit    time.Duration
	nonCriticalLimit time.Duration
	executionTime    time.Duration
	status           string
}

type FunctionControllerInterface interface {
	Exec(ctx context.Context, fun model.Function, err chan error, args ...interface{}) (interface{}, error)
	GetStatus() interface{}
}

func NewFunctionController(criticalLimit time.Duration, nonCriticalLimit time.Duration) *FunctionController {
	return &FunctionController{criticalLimit: criticalLimit,
		nonCriticalLimit: nonCriticalLimit}
}

// Exec is the function to control the execution of a function which executes some value.
// errChan is a channel that can be used to send non-critical errors back to the client.
func (controller *FunctionController) Exec(ctx context.Context, fun model.Function, errChan chan error, args ...interface{}) (interface{}, error) {
	// Create a channel to get the result of the function
	resultChan := make(chan interface{})
	criticalErrorChan := make(chan error)

	controller.status = "running"
	start := time.Now()

	// Run the function in a separate goroutine
	go func() {
		result, err := fun(errChan, args...)
		if err != nil {
			criticalErrorChan <- err
			return
		}
		resultChan <- result
	}()

	// Create a timer for the critical limit
	criticalTimer := time.NewTimer(controller.criticalLimit)

	// Create a timer for the non-critical limit
	nonCriticalTimer := time.NewTimer(controller.nonCriticalLimit)

	for {
		select {
		case <-ctx.Done():
			controller.status = "cancelled"
			return nil, ctx.Err()
		case <-nonCriticalTimer.C:
			errChan <- fmt.Errorf("non-critical error: function execution exceeded non-critical limit")
		case <-criticalTimer.C:
			controller.status = "timeout"
			return nil, fmt.Errorf("critical error: function execution exceeded critical limit")
		case err := <-criticalErrorChan:
			controller.status = "cancelled"
			return nil, err
		case result := <-resultChan:
			controller.status = "success"
			return result, nil
		default:
			controller.executionTime = time.Since(start)
		}
	}
}

type FunctionControllerStatus struct {
	CriticalLimit    time.Duration
	NonCriticalLimit time.Duration
	ExecutionTime    time.Duration
	Status           string
}

func (controller *FunctionController) GetStatus() FunctionControllerStatus {
	return FunctionControllerStatus{
		CriticalLimit:    controller.criticalLimit,
		NonCriticalLimit: controller.nonCriticalLimit,
		ExecutionTime:    controller.executionTime,
		Status:           controller.status,
	}
}

func (status *FunctionControllerStatus) Serialize() ([]byte, error) {
	var buf bytes.Buffer
	enc := gob.NewEncoder(&buf)
	err := enc.Encode(status)
	if err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
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

var functionController = NewFunctionController(config.DefaultCriticalErrorLimit, config.DefaultCriticalErrorLimit)
