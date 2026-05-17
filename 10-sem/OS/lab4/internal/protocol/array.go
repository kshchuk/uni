package protocol

import (
	"encoding/binary"
	"fmt"
	"io"
)

const HeaderSize = 4

func WriteArray(w io.Writer, data []int32) error {
	if len(data) > int(^uint32(0)) {
		return fmt.Errorf("array too large: %d elements", len(data))
	}
	header := make([]byte, HeaderSize)
	binary.LittleEndian.PutUint32(header, uint32(len(data)))
	if _, err := w.Write(header); err != nil {
		return err
	}
	if len(data) == 0 {
		return nil
	}
	payload := make([]byte, len(data)*4)
	for i, v := range data {
		binary.LittleEndian.PutUint32(payload[i*4:], uint32(v))
	}
	_, err := w.Write(payload)
	return err
}

func ReadArray(r io.Reader) ([]int32, error) {
	header := make([]byte, HeaderSize)
	if _, err := io.ReadFull(r, header); err != nil {
		return nil, err
	}
	n := binary.LittleEndian.Uint32(header)
	if n == 0 {
		return nil, nil
	}
	payload := make([]byte, int(n)*4)
	if _, err := io.ReadFull(r, payload); err != nil {
		return nil, err
	}
	out := make([]int32, n)
	for i := range out {
		out[i] = int32(binary.LittleEndian.Uint32(payload[i*4:]))
	}
	return out, nil
}

func BytesPerMessage(n int) int64 {
	return int64(HeaderSize + n*4)
}
