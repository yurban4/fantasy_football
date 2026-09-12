import polars as pl

def add_coverage_metrics(df):
    return df.with_columns([
        pl.col("coverage").fill_null("unknown")
    ])
