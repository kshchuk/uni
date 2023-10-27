package model

import (
	"testing"
)

func TestError(t *testing.T) {
	err := NewFatalError("Fatal error occurred")

	if !err.IsFatalError() {
		t.Errorf("Expected error to be fatal")
	}

	if err.IsNonFatalError() {
		t.Errorf("Expected error not to be non-fatal")
	}

	if err.ErrorString() != "Fatal error occurred" {
		t.Errorf("Expected error message to be 'Fatal error occurred'")
	}

	serialized := err.Serialize()
	deserialized := DeserializeError(serialized)

	if deserialized.ErrorString() != "Fatal error occurred" {
		t.Errorf("Expected deserialized error message to be 'Fatal error occurred'")
	}
}
