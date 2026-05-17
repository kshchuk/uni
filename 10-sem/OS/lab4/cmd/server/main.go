package main

import (
	"flag"
	"log"
	"net"
	"os"
	"os/signal"
	"sync/atomic"
	"syscall"
	"time"

	"lab4/internal/protocol"
	sortpkg "lab4/internal/sort"
)

func main() {
	addr := flag.String("addr", ":9504", "TCP listen address")
	flag.Parse()

	ln, err := net.Listen("tcp", *addr)
	if err != nil {
		log.Fatalf("listen: %v", err)
	}
	defer ln.Close()

	var shuttingDown atomic.Bool
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-stop
		log.Println("shutting down")
		shuttingDown.Store(true)
		ln.Close()
	}()

	log.Printf("server listening on %s", *addr)
	for {
		conn, err := ln.Accept()
		if err != nil {
			if shuttingDown.Load() {
				return
			}
			log.Printf("accept: %v", err)
			continue
		}
		go handleConn(conn)
	}
}

func handleConn(conn net.Conn) {
	defer conn.Close()
	remote := conn.RemoteAddr().String()

	data, err := protocol.ReadArray(conn)
	if err != nil {
		log.Printf("[%s] read: %v", remote, err)
		return
	}
	log.Printf("[%s] received %d elements", remote, len(data))

	t0 := time.Now()
	sortpkg.SortInPlace(data)
	sortDur := time.Since(t0)

	if err := protocol.WriteArray(conn, data); err != nil {
		log.Printf("[%s] write: %v", remote, err)
		return
	}
	log.Printf("[%s] sorted and replied (sort %v)", remote, sortDur)
}
