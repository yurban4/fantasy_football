import polars as pl

def add_play_action_motion(df):
    return df.with_columns([
        pl.col("motion").fill_null(False)
    ])
