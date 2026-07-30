#[path = "src/lib.rs"]
mod subject;

use subject::{parse_limit, ParseLimitError};

#[test]
fn parses_valid_limit() {
    assert_eq!(parse_limit("25"), Ok(25));
}

#[test]
fn reports_non_numeric_input() {
    assert_eq!(parse_limit("many"), Err(ParseLimitError::NotNumber));
}

