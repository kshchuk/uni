package model

import (
	"fmt"
	"time"
)

/*CalculateFactorial is a function that calculates the factorial of the N.
*
* errChan is a channel that can be used to send non-critical errors back to the controller.
 */
func CalculateFactorial(errChan chan error, args ...interface{}) (interface{}, error) {
	// Get the first argument and convert it to an integer
	n, ok := args[0].(int)
	if !ok {
		return nil, fmt.Errorf("invalid argument")
	}

	// Calculate the factorial
	fact := 1
	for i := 1; i <= n; i++ {
		fact *= i

		// Simulate a long-running task and non-critical errors
		time.Sleep(1 * time.Second)
		if i%10 == 0 {
			errChan <- fmt.Errorf("non-critical error occurred in CalculateFactorial")
		}
	}

	return fact, nil
}

/*CalculateFibonacci is a function that calculates the Nth Fibonacci number.
*
* errChan is a channel that can be used to send non-critical errors back to the controller.
 */
func CalculateFibonacci(errChan chan error, args ...interface{}) (interface{}, error) {
	// Get the first argument and convert it to an integer
	n, ok := args[0].(int)
	if !ok {
		return nil, fmt.Errorf("invalid argument")
	}

	// Calculate the Fibonacci number
	fib := 1
	for i, j := 0, 1; i < n; i, j = i+j, i {
		fib = i

		// Simulate a long-running task and non-critical errors
		time.Sleep(1 * time.Second)
		if i%10 == 0 {
			errChan <- fmt.Errorf("non-critical error occurred in CalculateFibonacci")
		}
	}

	return fib, nil
}
