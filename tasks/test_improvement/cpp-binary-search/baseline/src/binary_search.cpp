#include "binary_search.hpp"

int index_of(const std::vector<int>& values, int target) {
    if (values.empty()) {
        return -1;
    }
    std::size_t low = 0;
    std::size_t high = values.size() - 1;
    while (low < high) {
        const std::size_t middle = low + (high - low) / 2;
        if (values[middle] < target) {
            low = middle + 1;
        } else {
            high = middle - 1;
        }
    }
    return values[low] == target ? static_cast<int>(low) : -1;
}

