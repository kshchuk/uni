package controller

import (
	"bufio"
	"fmt"
	"lab-1/function-1/model"
	"lab-1/function-1/util"
	"net"
	"strings"
)

type Client struct {
	conn net.Conn
	data string
}

func NewClient(conn net.Conn) *Client {
	return &Client{conn: conn}
}

func (client *Client) HandleConnection() {
	fmt.Printf("Serving %s\n", client.conn.RemoteAddr().String())
	defer client.conn.Close()

	for {
		netData, err := bufio.NewReader(client.conn).ReadString('\n')
		if err != nil {
			fmt.Println(err)
			return
		}
		// TODO: remove this
		client.data = strings.TrimSpace(string(netData))
		if client.data == "STOP" {
			break
		}
		fmt.Println(client.data)
		client.conn.Write([]byte("OK\n"))
	}
	client.conn.Close()
}

func (client *Client) handleRequest(data []byte) (response []byte) {
	req, err := model.DeserializeRequest(data)
	if err != nil {
		return model.SerializedFatalErrorOrDie(err.Error())
	}

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
	args := []interface{}{data.Data}

	go func() {
		result, err := functionController.Exec(model.CalculateFactorial, errChan, args...)
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
			return model.NewDataRequest("int64", util.ToBytes(result.(int64))), nil
		case nonCriticalError := <-errChan:
			err := model.NewNonFatalError(nonCriticalError.Error())
			serialized, errorr := err.Serialize()
			if errorr != nil {
				return nil, model.NewFatalError(errorr.Error())
			}
			_, err2 := client.conn.Write(serialized)
			if err2 != nil {
				return nil, model.NewFatalError(err2.Error())
			}
		}
	}
}
