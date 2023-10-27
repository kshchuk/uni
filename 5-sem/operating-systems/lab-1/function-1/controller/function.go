package controller

import (
	"context"
	"fmt"
	"lab-1/function-1/model"
	"time"
)

type FunctionController struct {
	criticalLimit    time.Duration
	nonCriticalLimit time.Duration
}

type FunctionControllerInterface interface {
	Exec(ctx context.Context, fun model.Function, err chan error, args ...interface{}) (interface{}, error)
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
			return nil, ctx.Err()
		case <-nonCriticalTimer.C:
			errChan <- fmt.Errorf("non-critical error: function execution exceeded non-critical limit")
		case <-criticalTimer.C:
			return nil, fmt.Errorf("critical error: function execution exceeded critical limit")
		case err := <-criticalErrorChan:
			return nil, err
		case result := <-resultChan:
			return result, nil
		}
	}
}
