package util

import "unsafe"

func GetSize[T any]() uintptr {
	var v T
	return unsafe.Sizeof(v)
}

func ToBytes[T any](v T) []byte {
	return *(*[]byte)(unsafe.Pointer(&v))
}
