package model

/* Error is the base error type
 * Code 0 is success
 * Code 1 is non-fatal error
 * Code 2 is fatal error
 */

type Error struct {
	Response
	message string
}

type FatalError struct {
	Error
}

type NonFatalError struct {
	Error
	Data interface{}
}

func NewFatalError(message string) *FatalError {
	return &FatalError{
		Error{
			Response{
				code: 2,
			},
			message,
		},
	}
}

func NewNonFatalError(message string, data interface{}) *NonFatalError {
	return &NonFatalError{
		Error{
			Response{
				code: 1,
			},
			message,
		},
		data,
	}
}

func (e *Error) ErrorString() string {
	return e.message
}
