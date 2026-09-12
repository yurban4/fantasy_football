import polars as pl
import nflreadpy as nfl

def load_ftn_charting(seasons):
    if isinstance(seasons, int):
        seasons = [seasons]

    df = nfl.load_ftn_charting(seasons)
    df = df.with_columns([
        pl.col("nflverse_play_id").cast(pl.Int64),
        pl.col("nflverse_game_id").cast(pl.Utf8)
    ])
    df = df.rename({c: c.lower().replace(" ", "_") for c in df.columns})

    # Sicherstellen, dass die Keys existieren
    for col in ["nflverse_game_id", "nflverse_play_id"]:
        if col not in df.columns:
            raise ValueError(f"FTN charting data missing column: {col}")

    return df
