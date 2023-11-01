package controller

import (
	"net"
	"time"
)

type Server struct {
	clients []*Client
	addr    string
	ln      net.Listener
}

func NewServer(addr string) *Server {
	return &Server{addr: addr}
}

func (server *Server) Start() error {
	ln, err := net.Listen("tcp", server.addr)
	if err != nil {
		return err
	}
	server.ln = ln

	for {
		conn, err := ln.Accept()
		if err != nil {
			return err
		}
		conn.SetDeadline(time.Now().Add(100 * time.Second))

		client := NewClient(conn)
		server.AddClient(client)
		go client.HandleConnection()
	}

	return nil
}

func (server *Server) AddClient(client *Client) {
	server.clients = append(server.clients, client)
}

func (server *Server) RemoveClient(client *Client) {
	for i, c := range server.clients {
		if c == client {
			server.clients = append(server.clients[:i], server.clients[i+1:]...)
			return
		}
	}
}
