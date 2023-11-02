package config

import "time"

const (
	DefaultNonCriticalErrorLimit = time.Duration(5 * time.Second)
	DefaultCriticalErrorLimit    = time.Duration(30 * time.Second)
	DefaultPort                  = 8002
	DefaultHost                  = "localhost"
)

type Config struct {
	NonCriticalErrorLimit time.Duration
	CriticalErrorLimit    time.Duration
	Port                  int
	Host                  string
}

func NewConfig() *Config {
	return &Config{
		NonCriticalErrorLimit: DefaultNonCriticalErrorLimit,
		CriticalErrorLimit:    DefaultCriticalErrorLimit,
		Port:                  DefaultPort,
		Host:                  DefaultHost,
	}
}

var config = NewConfig()
