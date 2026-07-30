# Golden Explanation

The parser exposed messages as program state. A two-variant enum makes the contract exhaustive while `Display` preserves the human-facing wording. Parsing and range validation remain separate, no panic or unsafe block is introduced, and time and space remain O(1).

