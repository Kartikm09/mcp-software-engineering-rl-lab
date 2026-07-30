package dedupe

import (
	"reflect"
	"testing"
)

func TestPreservesFirstOccurrenceOrder(t *testing.T) {
	actual, checks := UniqueWithStats([]string{"z", "a", "z", "m", "a"})
	expected := []string{"z", "a", "m"}
	if !reflect.DeepEqual(actual, expected) {
		t.Fatalf("got %v, want %v", actual, expected)
	}
	if checks > 5 {
		t.Fatalf("membership checks = %d, want <= 5", checks)
	}
}

func BenchmarkUnique(b *testing.B) {
	values := make([]string, 1000)
	for i := range values {
		values[i] = string(rune('a' + (i % 20)))
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		UniqueWithStats(values)
	}
}

