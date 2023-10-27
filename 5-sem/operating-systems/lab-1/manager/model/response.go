package model

/* Request is the base response type
* Code 0 is success
* Code 1 is non-fatal error
* Code 2 is fatal error
 */

type Response struct {
	code uint8
}

type ResponseData struct {
	Response
	Data interface{}
}

func (r *Response) IsSuccess() bool {
	return r.code == 0
}

func (r *Response) IsNonFatalError() bool {
	return r.code == 1
}

func (r *Response) IsFatalError() bool {
	return r.code == 2
}

func NewResponseData(data interface{}) *ResponseData {
	return &ResponseData{
		Response{
			code: 0,
		},
		data,
	}
}
