import polars as pl

def add_proe(df):
    return df.with_columns([
        (pl.col("pass") - pl.col("pass").mean()).alias("proe")
    ])
