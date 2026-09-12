import polars as pl

def add_fantasy_rolling(df):
    fp = "fantasy_points" if "fantasy_points" in df.columns else "ff_points_total"

    for w in [3, 5, 8]:
        df = df.with_columns([
            pl.col(fp).rolling_mean(window_size=w).over("player_id").alias(f"{fp}_rollmean_{w}"),
            pl.col(fp).rolling_sum(window_size=w).over("player_id").alias(f"{fp}_rollsum_{w}")
        ])

    return df
