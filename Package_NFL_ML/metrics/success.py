import polars as pl

def add_success_metrics(df: pl.DataFrame) -> pl.DataFrame:
    if "down" not in df.columns:
        raise ValueError("Column 'down' missing — this is a PBP metric.")
    return df.with_columns([
        (pl.col("epa") > 0).alias("success")
    ])
