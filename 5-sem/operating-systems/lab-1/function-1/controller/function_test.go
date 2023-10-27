package controller

import (
	"context"
	"errors"
	"testing"
	"time"
)

func TestExec(t *testing.T) {
	errChan := make(chan error)
	go func() {
		for err := range errChan {
			t.Log(err)
		}
	}()

	ctx := context.Background()
	criticalLimit := 2 * time.Second
	nonCriticalLimit := 1 * time.Second
	controller := NewFunctionController(criticalLimit, nonCriticalLimit)

	fun := func(errChan chan error, args ...interface{}) (interface{}, error) {
		time.Sleep(500 * time.Millisecond)
		return "success", nil
	}

	result, err := controller.Exec(ctx, fun, errChan)
	if err != nil {
		t.Errorf("Unexpected error: %v", err)
	}
	if result != "success" {
		t.Errorf("Unexpected result: %v", result)
	}

	fun = func(errChan chan error, args ...interface{}) (interface{}, error) {
		time.Sleep(3 * time.Second)
		return nil, errors.New("function error")
	}

	result, err = controller.Exec(ctx, fun, errChan)
	if err == nil || err.Error() != "critical error: function execution exceeded critical limit" {
		t.Errorf("Expected critical limit error, got: %v", err)
	}

	fun = func(errChan chan error, args ...interface{}) (interface{}, error) {
		time.Sleep(1500 * time.Millisecond)
		errChan <- errors.New("non-critical function error")
		return "partial success", nil
	}

	result, err = controller.Exec(ctx, fun, errChan)
	if err != nil {
		t.Errorf("Unexpected error: %v", err)
	}
	if result != "partial success" {
		t.Errorf("Unexpected result: %v", result)
	}

	ctxWithCancel, cancelFunc := context.WithCancel(ctx)
	cancelFunc()

	fun = func(errChan chan error, args ...interface{}) (interface{}, error) {
		time.Sleep(500 * time.Millisecond)
		return "success", nil
	}

	result, err = controller.Exec(ctxWithCancel, fun, errChan)
	if err == nil || err.Error() != "context canceled" {
		t.Errorf("Expected context canceled error, got: %v", err)
	}
}
