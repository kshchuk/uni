package sortpkg

import (
	"math/rand"
	"testing"
)

func TestSortInPlace(t *testing.T) {
	data := []int32{5, 1, 4, 2, 8, 0, 2}
	SortInPlace(data)
	for i := 1; i < len(data); i++ {
		if data[i] < data[i-1] {
			t.Fatalf("not sorted at %d: %v", i, data)
		}
	}
}

func TestSortInPlaceRandom(t *testing.T) {
	rng := rand.New(rand.NewSource(1))
	data := make([]int32, 5000)
	for i := range data {
		data[i] = rng.Int31()
	}
	SortInPlace(data)
	for i := 1; i < len(data); i++ {
		if data[i] < data[i-1] {
			t.Fatal("not sorted")
		}
	}
}
