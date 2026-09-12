import polars as pl

def add_red_zone_metrics(df):
    return df.with_columns([
        (pl.col("yardline_100") <= 20).alias("red_zone")
    ])
