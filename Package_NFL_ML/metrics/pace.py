import polars as pl

def add_pace(df):
    return df.with_columns([
        pl.col("time_to_snap").alias("pace")
    ])
