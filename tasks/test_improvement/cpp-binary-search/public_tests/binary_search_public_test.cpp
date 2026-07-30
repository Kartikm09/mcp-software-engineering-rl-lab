#include "src/binary_search.hpp"

#include <cassert>
#include <vector>

int main() {
    const std::vector<int> values{1, 3, 5, 7, 9};
    assert(index_of(values, 1) == 0);
    assert(index_of(values, 7) == 3);
    return 0;
}

