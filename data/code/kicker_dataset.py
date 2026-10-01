import nflreadpy as nfl
import polars as pl
import numpy as np

seasons = [2022, 2023, 2024, 2025, 2026]

df_kick = (
    nfl.load_team_stats( # PFR Passing Stats
        seasons=seasons,
        summary_level="week"
    ).select(
        "game_id", "team", "week", "season",
        "passing_2pt_conversions", "rushing_2pt_conversions",
    )
).join( # Join Player Stats
    nfl.load_player_stats(
        seasons=seasons,
        summary_level="week"
    ).select(
        "player_id", "season", "week", "team",
        "fg_made", "fg_missed", "fg_att", "fg_blocked",
        "fg_made_0_19", "fg_made_20_29", "fg_made_30_39",
        "fg_made_40_49", "fg_made_50_59", "fg_made_60_",
        "fg_missed_0_19", "fg_missed_20_29", "fg_missed_30_39",
        "fg_missed_40_49", "fg_missed_50_59", "fg_missed_60_",
        "pat_att", "pat_missed", "pat_blocked", "pat_pct", 'pat_made',
        "gwfg_made", "gwfg_att"
    ), how="left", left_on=["team", "season", "week"], right_on=["team", "season", "week"]
).drop_nulls()

# Fantasy Football Points Calculation
df_kick = df_kick.with_columns(
    (df_kick["pat_made"] * 1).alias("ff_points_pat"),
    ((df_kick["fg_made_0_19"] + df_kick["fg_made_20_29"] + df_kick["fg_made_30_39"]) * 3 ).alias("ff_points_fg_0_39"),
    (df_kick["fg_made_40_49"] * 4).alias("ff_points_fg_40_49"),
    ((df_kick["fg_made_50_59"] + df_kick["fg_made_60_"]) * 5).alias("ff_points_fg_50_")
)
df_kick = df_kick.with_columns(
    (df_kick["ff_points_pat"] +  df_kick["ff_points_fg_0_39"] + df_kick["ff_points_fg_40_49"] + df_kick["ff_points_fg_50_"]).alias("ff_points_total"),
)


print(df_kick)
df_kick.write_csv("data/raw/kick_stats.csv", decimal_comma=True, separator=";")