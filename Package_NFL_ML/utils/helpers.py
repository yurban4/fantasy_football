import polars as pl

def ensure_polars(df):
    if not isinstance(df, pl.DataFrame):
        raise TypeError("Expected a Polars DataFrame")
    return df

def safe_divide(a, b):
    return a / b if b not in (0, None) else None

def filter_regular_season(df):
    return df.filter(pl.col("week") <= 18)
