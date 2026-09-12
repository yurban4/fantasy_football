import polars as pl

def add_team_rolling_epa(df):
    return df.with_columns([
        pl.col("epa").rolling_mean(window_size=20).over("posteam").alias("team_epa_rolling")
    ])
