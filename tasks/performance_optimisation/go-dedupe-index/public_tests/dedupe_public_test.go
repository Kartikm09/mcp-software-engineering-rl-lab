package dedupe

import (
	"reflect"
	"testing"
)

func TestUniqueValues(t *testing.T) {
	actual, _ := UniqueWithStats([]string{"a", "a", "b", "b"})
	expected := []string{"a", "b"}
	if !reflect.DeepEqual(actual, expected) {
		t.Fatalf("got %v, want %v", actual, expected)
	}
}

