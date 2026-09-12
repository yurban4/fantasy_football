import polars as pl

def add_box_advantage(df):
    return df.with_columns([
        pl.col("box").fill_null(0)
    ])
