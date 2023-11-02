package controller

import (
	"bytes"
	"context"
	"encoding/gob"
	"fmt"
	"lab-1/function-2/config"
	"lab-1/function-2/model"
	"time"
)

type FunctionController struct {
	criticalLimit    time.Duration
	nonCriticalLimit time.Duration
	executionTime    time.Duration
	status           string
	ctx              context.Context
	cancel           context.CancelFunc
}

type FunctionControllerInterface interface {
	Exec(ctx context.Context, fun model.Function, err chan error, args ...interface{}) (interface{}, error)
	GetStatus() interface{}
}

func NewFunctionController(criticalLimit time.Duration, nonCriticalLimit time.Duration) *FunctionController {
	ctx := context.Background()
	ctx, cancel := context.WithCancel(ctx)
	return &FunctionController{
		criticalLimit:    criticalLimit,
		nonCriticalLimit: nonCriticalLimit,
		executionTime:    time.Duration(0),
		status:           "idle",
		ctx:              ctx,
		cancel:           cancel,
	}
}

func (controller *FunctionController) SetNewContext() {
	ctx := context.Background()
	ctx, cancel := context.WithCancel(ctx)
	controller.ctx = ctx
	controller.cancel = cancel
}

func (controller *FunctionController) Cancel() {
	controller.cancel()
}

// Exec is the function to control the execution of a function which executes some value.
// errChan is a channel that can be used to send non-critical errors back to the client.
func (controller *FunctionController) Exec(fun model.Function, errChan chan error, args ...interface{}) (interface{}, error) {
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
		case <-controller.ctx.Done():
			controller.status = "cancelled"
			return nil, controller.ctx.Err()
		case <-nonCriticalTimer.C:
			errChan <- fmt.Errorf("non-critical error: function execution exceeded non-critical limit")
		case <-criticalTimer.C:
			controller.status = "timeout"
			status := controller.GetStatus()
			return nil, fmt.Errorf("critical error: function execution exceeded critical limit, status: %s", status.String())
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

func (status *FunctionControllerStatus) String() string {
	return "FunctionControllerStatus{CriticalLimit: " + status.CriticalLimit.String() + ", NonCriticalLimit: " + status.NonCriticalLimit.String() + ", ExecutionTime: " + status.ExecutionTime.String() + ", Status: " + status.Status + "}"
}

var functionController = NewFunctionController(config.DefaultCriticalErrorLimit, config.DefaultNonCriticalErrorLimit)
