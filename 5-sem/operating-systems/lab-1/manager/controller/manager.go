package controller

import (
	"context"
	"fmt"
	"lab-1/function-1/util"
	"lab-1/manager/model"
	"net"
	"time"
)

type ManagerController struct {
	function1 net.Conn
	function2 net.Conn

	status     string
	resultChan chan *model.RequestData
	ctx        context.Context
	cancel     context.CancelFunc
}

type ManagerControllerInterface interface {
	InitConnections(address1, address2 string) error
	StartManager() error
	StartComputations(arg int64) error
	GetComputationStatuses() error
	CancelComputations() error
}

func (manager *ManagerController) InitConnections(address1, address2 string) error {
	manager.status = "Initializing connection"
	var err error
	manager.function1, err = net.Dial("tcp", address1)
	if err != nil {
		return err
	}

	manager.function2, err = net.Dial("tcp", address2)
	if err != nil {
		return err
	}

	manager.status = "Connection initialized"
	return nil
}

func (manager *ManagerController) StartManager() error {
	manager.status = "Starting manager"
	manager.resultChan = make(chan *model.RequestData, 2)

	go manager.listenFunction(manager.function1)
	go manager.listenFunction(manager.function2)

	manager.status = "Manager started"
	return nil
}

func (manager *ManagerController) listenFunction(c net.Conn) {
	for {
		buf := make([]byte, 1024)
		n, err := c.Read(buf)
		if err != nil {
			fmt.Println(err)
			return
		}
		data := buf[:n]

		go func() {
			response, err := manager.handleRequest(data)
			if err != nil {
				fmt.Println(err)
			}
			fmt.Printf("Connecttion %s\n", c.RemoteAddr().String())

			switch response.(type) {
			case *model.RequestData:
				manager.resultChan <- response.(*model.RequestData)
			case *model.Error:
				err := response.(*model.Error)
				fmt.Println(err.ErrorString())
				if err.IsFatalError() {
					manager.cancel()
				}
			case string: // Status
				fmt.Println(response.(string))
			}
		}()
	}
}

func (manager *ManagerController) StartComputations(arg int64) error {
	manager.status = "Starting computations"
	manager.ctx = context.Background()
	manager.ctx, manager.cancel = context.WithCancel(manager.ctx)

	err := manager.startComputation(arg, manager.function1)
	if err != nil {
		return err
	}
	err = manager.startComputation(arg, manager.function2)
	if err != nil {
		return err
	}

	manager.status = "Computations started"

	go manager.handleResults()
	return nil
}

func (manager *ManagerController) startComputation(arg int64, c net.Conn) error {
	argData, err := util.ToBytes(arg)
	if err != nil {
		return err
	}
	request := model.NewDataRequest("int64", argData)
	requestSerialized, err := request.Serialize()
	req, err := model.DeserializeRequestData(requestSerialized)
	fmt.Printf("_____________________________________________________________\nRequest sent:\n Code %d\n Time %s\n Content type %s\n Data size %d\n Data %d\n", req.Code, time.Unix(0, req.Time).String(), request.ContentType, request.DataSize, arg)
	fmt.Printf("Connecttion %s\n", c.RemoteAddr().String())
	if err != nil {
		return err
	}
	_, err = c.Write(requestSerialized)
	if err != nil {
		return err
	}
	return nil
}

func (manager *ManagerController) handleResults() {
	results := make([]*model.RequestData, 2)
	var result int64 = 0

	for i := 0; i < 2; i++ {
		select {
		case results[i] = <-manager.resultChan:
			res, err := util.FromBytes(results[i].Data)
			if err != nil {
				fmt.Println(err)
				return
			}
			fmt.Printf("_____________________________________________________________\nResult received:\n Code %d\n Time %s\n Content type %s\n Data size %d\n Data %d\n",
				results[i].Code, time.Unix(0, results[i].Time).String(), results[i].ContentType, results[i].DataSize, res)
			result += res
		case <-manager.ctx.Done():
			return
		}
	}
	fmt.Printf("_____________________________________________________________\nResult: %d\n", result)
}

func (manager *ManagerController) handleRequest(data []byte) (interface{}, error) {
	req, err := model.DeserializeRequest(data)
	if err != nil {
		return nil, err
	}

	fmt.Printf("_____________________________________________________________\nReceived request:\n Code %d\n Time %s\n", req.Code, time.Unix(0, req.Time).String())

	switch {
	case req.IsStatusRequest():
		reqData, err := model.DeserializeRequestData(data)
		if err != nil {
			return nil, err
		}
		status, err := model.DeserializeFunctionControllerStatus(reqData.Data)
		if err != nil {
			return nil, err
		}
		return status.String(), nil
	case req.IsDataRequest():
		reqData, err := model.DeserializeRequestData(data)
		if err != nil {
			return nil, err
		}
		return reqData, nil
	case req.IsNonFatalError():
		reqData, err := model.DeserializeError(data)
		if err != nil {
			return nil, err
		}
		return reqData, nil
	case req.IsFatalError():
		reqData, err := model.DeserializeError(data)
		if err != nil {
			return nil, err
		}
		manager.CancelComputations()
		return reqData, nil
	default:
		panic("Unknown request type")
	}

	return nil, nil
}

func (manager *ManagerController) GetComputationStatuses() error {
	err := manager.getStatus(manager.function1)
	if err != nil {
		return err
	}
	err = manager.getStatus(manager.function2)
	if err != nil {
		return err
	}
	return nil
}

func (manager *ManagerController) getStatus(c net.Conn) error {
	// Send status request
	request := model.NewStatusRequest()
	requestSerialized, err := request.Serialize()
	if err != nil {
		return err
	}
	_, err = c.Write(requestSerialized)
	if err != nil {
		return err
	}
	fmt.Printf("_____________________________________________________________\nRequest sent:\n Code %d\n Time %s\n", request.Code, time.Unix(0, request.Time).String())
	fmt.Printf("Connecttion %s\n", c.RemoteAddr().String())
	return nil
}

func (manager *ManagerController) CancelComputations() error {
	manager.status = "Canceling computations"
	err := manager.cancelComputations()
	manager.cancel()

	if err != nil {
		return err
	}
	fmt.Println("Computations canceled")
	manager.status = "Computations canceled"
	return nil
}

// Send cancel requests to both functions
func (manager *ManagerController) cancelComputations() error {
	request := model.NewCancelRequest()
	requestSerialized, err := request.Serialize()
	if err != nil {
		return err
	}

	var e error = nil
	_, err = manager.function1.Write(requestSerialized)
	if err != nil {
		e = err
	}
	fmt.Printf("_____________________________________________________________\nRequest sent:\n Code %d\n Time %s\n", request.Code, time.Unix(0, request.Time).String())
	fmt.Printf("Connecttion %s\n", manager.function1.RemoteAddr().String())

	_, err = manager.function2.Write(requestSerialized)
	if err != nil {
		e = err
	}
	fmt.Printf("_____________________________________________________________\nRequest sent:\n Code %d\n Time %s\n", request.Code, time.Unix(0, request.Time).String())
	fmt.Printf("Connecttion %s\n", manager.function2.RemoteAddr().String())

	manager.status = "Computations canceled"
	return e
}
