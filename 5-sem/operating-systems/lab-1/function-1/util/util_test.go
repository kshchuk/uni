package util

import (
	"reflect"
	"testing"
)

func TestGetSize(t *testing.T) {
	var tests = []struct {
		input    interface{}
		expected uintptr
	}{
		{int(1), 8},
		{uint(1), 8},
		{float32(1.0), 4},
	}

	for _, tt := range tests {
		testname := reflect.TypeOf(tt.input).Name()
		t.Run(testname, func(t *testing.T) {
			ans := GetSize(tt.input)
			if ans != tt.expected {
				t.Errorf("got %v, want %v", ans, tt.expected)
			}
		})
	}
}

func TestToBytesAndFromBytes(t *testing.T) {
	var tests = []struct {
		input    int64
		expected int64
	}{
		{int64(1), int64(1)},
		{int64(0), int64(0)},
		{int64(-1), int64(-1)},
		{int64(1234567890), int64(1234567890)},
	}

	for _, tt := range tests {
		testname := "ToBytesAndFromBytes"
		t.Run(testname, func(t *testing.T) {
			bytes, _ := ToBytes(tt.input)
			ans, _ := FromBytes(bytes)
			if ans != tt.expected {
				t.Errorf("got %v, want %v", ans, tt.expected)
			}
		})
	}
}
