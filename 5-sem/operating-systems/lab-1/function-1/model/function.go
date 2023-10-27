package model

import (
	"fmt"
	"time"
)

type Function func(errChan chan error, args ...interface{}) (interface{}, error)

/*
Function1 is the function that will be executed to compute some value.

errChan is a channel that can be used to send non-critical errors back to the controller.
*/
func Function1(errChan chan error, args ...interface{}) (interface{}, error) {
	time.Sleep(5 * time.Second) // simulate long running task

	errChan <- fmt.Errorf("non-critical error occurred")

	time.Sleep(5 * time.Second) // simulate long running task
	return args[0], nil
}
