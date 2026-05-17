package main

import (
	"flag"
	"fmt"
	"log"
	"math"
	"math/rand"
	"net"
	"time"

	"lab4/internal/protocol"
)

func main() {
	addr := flag.String("addr", "127.0.0.1:9504", "server address")
	n := flag.Int("n", 10000, "array length")
	runs := flag.Int("runs", 100, "number of experiments")
	seed := flag.Int64("seed", 42, "RNG seed base")
	flag.Parse()

	if *n <= 0 {
		log.Fatal("n must be positive")
	}
	if *runs <= 0 {
		log.Fatal("runs must be positive")
	}

	rtts := make([]time.Duration, *runs)
	bytesPerRun := 2 * protocol.BytesPerMessage(*n)

	fmt.Printf("Lab 4 client: addr=%s n=%d runs=%d seed=%d\n", *addr, *n, *runs, *seed)
	fmt.Printf("Bytes per round-trip (request+response): %d\n\n", bytesPerRun)

	for i := 0; i < *runs; i++ {
		data := randomArray(*n, *seed+int64(i))
		dur, err := roundTrip(*addr, data)
		if err != nil {
			log.Fatalf("run %d: %v", i+1, err)
		}
		if !isSorted(data) {
			log.Fatalf("run %d: server returned unsorted array", i+1)
		}
		rtts[i] = dur
	}

	avg, min, max, std := stats(rtts)
	avgSec := avg.Seconds()
	mbps := float64(bytesPerRun) * 8 / avgSec / 1e6

	fmt.Printf("=== Results (%d experiments) ===\n", *runs)
	fmt.Printf("RTT avg:  %v\n", avg)
	fmt.Printf("RTT min:  %v\n", min)
	fmt.Printf("RTT max:  %v\n", max)
	fmt.Printf("RTT stdev: %v\n", std)
	fmt.Printf("Average port speed: %.2f Mbit/s\n", mbps)
	fmt.Printf("Average port speed: %.2f MB/s\n", float64(bytesPerRun)/avgSec/1e6)
}

func roundTrip(addr string, data []int32) (time.Duration, error) {
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return 0, err
	}
	defer conn.Close()

	t0 := time.Now()
	if err := protocol.WriteArray(conn, data); err != nil {
		return 0, err
	}
	sorted, err := protocol.ReadArray(conn)
	if err != nil {
		return 0, err
	}
	t1 := time.Now()

	copy(data, sorted)
	return t1.Sub(t0), nil
}

func randomArray(n int, seed int64) []int32 {
	rng := rand.New(rand.NewSource(seed))
	out := make([]int32, n)
	for i := range out {
		out[i] = rng.Int31()
	}
	return out
}

func isSorted(data []int32) bool {
	for i := 1; i < len(data); i++ {
		if data[i] < data[i-1] {
			return false
		}
	}
	return true
}

func stats(rtts []time.Duration) (avg, min, max, std time.Duration) {
	if len(rtts) == 0 {
		return
	}
	min, max = rtts[0], rtts[0]
	var sum int64
	for _, d := range rtts {
		sum += d.Nanoseconds()
		if d < min {
			min = d
		}
		if d > max {
			max = d
		}
	}
	avg = time.Duration(sum / int64(len(rtts)))
	var varSum float64
	avgNs := float64(avg.Nanoseconds())
	for _, d := range rtts {
		diff := float64(d.Nanoseconds()) - avgNs
		varSum += diff * diff
	}
	std = time.Duration(math.Sqrt(varSum / float64(len(rtts))))
	return
}
