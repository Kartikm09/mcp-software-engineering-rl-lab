pub fn parse_limit(raw: &str) -> Result<u32, String> {
    let value = raw
        .parse::<u32>()
        .map_err(|_| "limit must be a number".to_string())?;
    if value == 0 || value > 1000 {
        return Err("limit must be between 1 and 1000".to_string());
    }
    Ok(value)
}

