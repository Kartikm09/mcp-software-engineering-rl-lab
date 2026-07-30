#[path = "src/lib.rs"]
mod subject;

use subject::{parse_limit, ParseLimitError};

#[test]
fn distinguishes_out_of_range() {
    assert_eq!(parse_limit("0"), Err(ParseLimitError::OutOfRange));
    assert_eq!(parse_limit("1001"), Err(ParseLimitError::OutOfRange));
}

#[test]
fn display_contract_is_stable() {
    assert_eq!(ParseLimitError::NotNumber.to_string(), "limit must be a number");
    assert_eq!(
        ParseLimitError::OutOfRange.to_string(),
        "limit must be between 1 and 1000"
    );
}

