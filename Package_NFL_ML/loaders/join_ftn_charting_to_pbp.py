import polars as pl

def join_ftn_charting_to_pbp(pbp: pl.DataFrame, ftn: pl.DataFrame) -> pl.DataFrame:
    pbp = pbp.rename({c: c.lower() for c in pbp.columns})
    ftn = ftn.rename({c: c.lower() for c in ftn.columns})

    required_pbp = ["game_id", "play_id"]
    required_ftn = ["nflverse_game_id", "nflverse_play_id"]

    for col in required_pbp:
        if col not in pbp.columns:
            raise ValueError(f"PBP missing join key: {col}")
    for col in required_ftn:
        if col not in ftn.columns:
            raise ValueError(f"FTN charting missing join key: {col}")

    return pbp.join(
        ftn,
        left_on=["game_id", "play_id"],
        right_on=["nflverse_game_id", "nflverse_play_id"],
        how="left",
    )
