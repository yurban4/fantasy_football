import nflreadpy as nfl
import polars as pl
import numpy as np

seasons = [2022, 2023, 2024, 2025, 2026]

df_match_scorings = pl.read_csv(
    "data/raw/team_game_data_2026.csv", separator=";", decimal_comma=True
).drop_nulls()
print(df_match_scorings)

df_def = (
    nfl.load_team_stats( # PFR Passing Stats
        seasons=seasons,
        summary_level="week"
    ).select(
        "game_id", "team", "week", "season",
        "def_tackles_solo", "def_tackles_with_assist", "def_tackle_assists",
        "def_tackles_for_loss", "def_tackles_for_loss_yards",
        "def_fumbles_forced", "def_sacks", "def_sack_yards",
        "def_qb_hits", 
        "def_interceptions", "def_interception_yards", "def_pass_defended",
        "def_tds", "def_safeties", "fumble_recovery_opp"
        )
).unique().join( # Join Opponent Scores
    df_match_scorings.select(
        "game_id", "team", "opp_score"
    ), how="left", left_on = ["game_id", "team"], right_on = ["game_id", "team"]
)
# Fantasy Football Points Calculation
df_def = df_def.with_columns(
    (df_def["def_interceptions"] * 2).alias("ff_points_interceptions"),
    (df_def["def_tds"] * 6).alias("ff_points_tds"),
    (df_def["def_sacks"] * 1).alias("ff_points_sacks"),
    (df_def["def_safeties"] * 2).alias("ff_points_safeties"),
    (df_def["fumble_recovery_opp"] * 2).alias("ff_points_fumble_recovery_opp"),
    pl.when(df_def["opp_score"] <= 6).then(10)
      .when(df_def["opp_score"] <= 13).then(7)
      .when(df_def["opp_score"] <= 20).then(4)
      .when(df_def["opp_score"] <= 27).then(1)
      .when(df_def["opp_score"] <= 34).then(-1)
      .otherwise(-4)
      .alias("ff_points_opp_score"),
)


print(df_def)
#df_qb.write_csv("advstats_2026.csv", decimal_comma=True, separator=";")