package main

import (
	"fmt"
	"lab-1/manager/controller"
)

func main() {
	manager := controller.ManagerController{}
	manager.InitConnections("localhost:8001", "localhost:8002")
	manager.StartManager()
	manager.StartComputations(5)

	var str string
	fmt.Scanln(&str)
}
