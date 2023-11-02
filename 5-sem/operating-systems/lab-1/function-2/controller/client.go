package controller

import (
	"fmt"
	"lab-1/function-2/model"
	"lab-1/function-2/util"
	"net"
	"time"
)

type Client struct {
	id   int
	conn net.Conn
}

func NewClient(conn net.Conn) *Client {
	return &Client{conn: conn}
}

func (client *Client) HandleConnection() {
	fmt.Printf("Serving %s\n", client.conn.RemoteAddr().String())
	defer client.conn.Close()
	buf := make([]byte, 1024)

	for {
		n, err := client.conn.Read(buf)
		if err != nil {
			fmt.Println(err)
			return
		}
		data := buf[:n]

		go func() {
			response := client.handleRequest(data)
			if response != nil {
				_, err := client.conn.Write(response)
				if err != nil {
					fmt.Println(err)
				}
			}
		}()
	}
}

func (client *Client) handleRequest(data []byte) (response []byte) {
	req, err := model.DeserializeRequest(data)
	if err != nil {
		return model.SerializedFatalErrorOrDie(err.Error())
	}

	fmt.Printf("Received request:\n Code %i\n Time: %s\n", req.Code, time.Unix(0, req.Time).String())

	switch {
	case req.IsStatusRequest():
		status := functionController.GetStatus()
		serialized, e := status.Serialize()
		var res model.Serializable = model.NewStatusRequestData(serialized)
		ser, e := res.Serialize()
		if e != nil {
			return model.SerializedFatalErrorOrDie(e.Error())
		}
		return ser
	case req.IsCancelRequest():
		functionController.Cancel()
		functionController.SetNewContext()
		return nil
	case req.IsDataRequest():
		reqData, err := model.DeserializeRequestData(data)
		if err != nil {
			return model.SerializedFatalErrorOrDie(err.Error())
		}

		resp, erro := client.execFunction(reqData)
		if erro != nil {
			var errorr error
			var e []byte
			e, errorr = erro.Serialize()
			if errorr != nil {
				return model.SerializedFatalErrorOrDie(errorr.Error())
			}
			return e
		}

		respser, err := resp.Serialize()
		if err != nil {
			return model.SerializedFatalErrorOrDie(err.Error())
		}
		return respser
	default:
		return model.SerializedFatalErrorOrDie("unknown request type")
	}
}

func (client *Client) execFunction(data *model.RequestData) (resp model.Serializable, e model.Serializable) {
	errChan := make(chan error)
	criticalErrorChan := make(chan error)
	resultChan := make(chan interface{})
	arg, err := util.FromBytes(data.Data)
	if err != nil {
		return nil, model.NewFatalError(err.Error())
	}
	args := []interface{}{arg}

	go func() {
		result, err := functionController.Exec(model.CalculateFibonacci, errChan, args...)
		if err != nil {
			criticalErrorChan <- err
			return
		}
		resultChan <- result
	}()

	for {
		select {
		case criticalError := <-criticalErrorChan:
			return nil, model.NewFatalError(criticalError.Error())
		case result := <-resultChan:
			resultBytes, err := util.ToBytes(result.(int64))
			if err != nil {
				return nil, model.NewFatalError(err.Error())
			}
			fmt.Printf("Sent result: %d\n", result)
			return model.NewDataRequest("int64", resultBytes), nil
		case nonCriticalError := <-errChan:
			err := model.NewNonFatalError(nonCriticalError.Error())
			serialized, errorr := err.Serialize()
			if errorr != nil {
				return nil, model.NewFatalError(errorr.Error())
			}
			_, err2 := client.conn.Write(serialized)
			fmt.Printf("Sent error: %s\n", err.ErrorString())
			if err2 != nil {
				return nil, model.NewFatalError(err2.Error())
			}
		}
	}
}
