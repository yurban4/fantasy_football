import polars as pl

def add_team_rolling_pace(df):
    return df.with_columns([
        pl.col("pace").rolling_mean(window_size=20).over("posteam").alias("team_pace_rolling")
    ])
