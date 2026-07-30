package dedupe

func UniqueWithStats(values []string) ([]string, int) {
	result := make([]string, 0, len(values))
	comparisons := 0
	for _, value := range values {
		duplicate := false
		for _, existing := range result {
			comparisons++
			if existing == value {
				duplicate = true
				break
			}
		}
		if !duplicate {
			result = append(result, value)
		}
	}
	return result, comparisons
}

