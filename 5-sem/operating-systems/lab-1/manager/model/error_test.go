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

	serialized, e := err.Serialize()
	if e != nil {
		t.Errorf("Unexpected error: %v", e)
	}
	deserialized, e := DeserializeError(serialized)
	if e != nil {
		t.Errorf("Unexpected error: %v", e)
	}

	if deserialized.ErrorString() != "Fatal error occurred" {
		t.Errorf("Expected deserialized error message to be 'Fatal error occurred'")
	}
}
