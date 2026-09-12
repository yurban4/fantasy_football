import polars as pl
import nflreadpy as nfl

def load_pbp_for_season(season: int) -> pl.DataFrame:
    df = nfl.load_pbp(season)  # returns Polars DataFrame
    df = df.with_columns([
        pl.col("play_id").cast(pl.Int64),
        pl.col("game_id").cast(pl.Utf8)
    ])

    return df
