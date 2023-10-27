package model

type Function func(errChan chan error, args ...interface{}) (interface{}, error)
