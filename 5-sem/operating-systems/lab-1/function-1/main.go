package main

import (
	"bufio"
	"fmt"
	"log"
	"net"
	"strings"
	"time"
)

func handleRequest(conn net.Conn) {
	defer conn.Close()

	reader := bufio.NewReader(conn)
	for {
		message, err := reader.ReadString('\n')
		if err != nil {
			log.Printf("Failed to read from client: %v", err)
			return
		}

		message = strings.TrimSpace(message)
		log.Printf("Received message: %s", message)

		go func() {
			time.Sleep(3 * time.Second)

			response := fmt.Sprintf("Message received: %s\n", message)
			if _, err := conn.Write([]byte(response)); err != nil {
				log.Printf("Failed to write to client: %v", err)
			}
		}()
	}
}

func main() {
	listener, err := net.Listen("tcp", "localhost:8080")
	if err != nil {
		log.Fatalf("Failed to listen on localhost:8080: %v", err)
	}
	defer listener.Close()

	log.Println("Listening on localhost:8080")

	for {
		conn, err := listener.Accept()
		if err != nil {
			log.Printf("Failed to accept connection: %v", err)
			continue
		}

		go handleRequest(conn)
	}
}
