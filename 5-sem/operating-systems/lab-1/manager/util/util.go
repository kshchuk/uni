package util

import (
	"bytes"
	"encoding/gob"
	"reflect"
)

func GetSize[T any](v T) uintptr {
	rv := reflect.ValueOf(v)
	return rv.Type().Size()
}

func ToBytes(v int64) ([]byte, error) {
	var buf bytes.Buffer
	enc := gob.NewEncoder(&buf)
	err := enc.Encode(v)
	if err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

func FromBytes(data []byte) (int64, error) {
	var v int64
	buf := bytes.NewBuffer(data)
	dec := gob.NewDecoder(buf)
	err := dec.Decode(&v)
	if err != nil {
		return 0, err
	}
	return v, nil
}
