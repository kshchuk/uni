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
	GetConnectionStatuses() string
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
	manager.ctx = context.Background()
	manager.ctx, manager.cancel = context.WithCancel(manager.ctx)

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

		// For canceling listening
		select {
		case <-manager.ctx.Done():
			return
		default:
			continue
		}
	}
}

func (manager *ManagerController) StartComputations(arg int64) error {
	manager.status = "Starting computations"

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
	fmt.Printf("Request sent:\n Code %d\n Time %s\n Content type %s\n Data size %d\n Data %d\n", req.Code, time.Unix(0, req.Time).String(), request.ContentType, request.DataSize, arg)
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
				continue
			}
			fmt.Printf("Request received:\n Code %d\n Time %s\n Content type %s\n Data size %d\n Data %d\n",
				results[i].Code, time.Unix(0, results[i].Time).String(), results[i].ContentType, results[i].DataSize, res)
			result += res
		case <-manager.ctx.Done():
			return
		}
	}
	fmt.Printf("Result: %d\n", result)
}

func (manager *ManagerController) handleRequest(data []byte) (interface{}, error) {
	req, err := model.DeserializeRequest(data)
	if err != nil {
		return nil, err
	}

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
		return reqData, nil
	default:
		panic("Unknown request type")
	}

	return nil, nil
}
