package util

import "unsafe"

func GetSize[T any]() uintptr {
	var v T
	return unsafe.Sizeof(v)
}
