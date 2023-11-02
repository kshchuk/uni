package main

import (
	"lab-1/function-2/controller"
	"net"
)

func main() {
	addr, err := net.ResolveTCPAddr("tcp", ":8001")

	if err != nil {
		panic(err)
	}

	server := controller.NewServer(addr.String())
	err = server.Start()
	if err != nil {
		panic(err)
	}
}
