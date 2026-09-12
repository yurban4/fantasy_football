import polars as pl

def rolling(df, col, window, group="player_id"):
    return (
        df.sort(["player_id", "week"])
          .with_columns([
              pl.col(col)
              .rolling_mean(window_size=window)
              .over(group)
              .alias(f"{col}_rollmean_{window}")
          ])
    )
