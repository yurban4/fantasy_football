import polars as pl

def add_pressure_metrics(df):
    return df.with_columns([
        pl.col("pressure").fill_null(0)
    ])
