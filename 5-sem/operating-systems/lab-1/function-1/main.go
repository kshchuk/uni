package main

import (
	"lab-1/function-1/controller"
	"net"
)

func main() {
	addr, err := net.ResolveTCPAddr("tcp", ":8002")
	if err != nil {
		panic(err)
	}

	server := controller.NewServer(addr.String())
	err = server.Start()
	if err != nil {
		panic(err)
	}
}
