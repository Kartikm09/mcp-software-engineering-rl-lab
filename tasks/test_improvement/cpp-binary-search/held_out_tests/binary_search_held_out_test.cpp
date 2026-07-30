#include "src/binary_search.hpp"

#include <cassert>
#include <vector>

int main() {
    const std::vector<int> values{1, 3, 5, 7, 9};
    assert(index_of(values, 9) == 4);
    assert(index_of(values, 4) == -1);
    assert(index_of({}, 4) == -1);
    return 0;
}

