import nflreadpy as nfl
import polars as pl
import numpy as np

seasons = [2022, 2023,2024, 2025, 2026]
df_qb = (
    nfl.load_pfr_advstats( # PFR Passing Stats
        seasons=seasons,
        stat_type="pass",
        summary_level="week"
    ).select(
        "game_id", "pfr_player_id", "team", "opponent", "week", "season",
        "passing_drops", "passing_drop_pct", "passing_bad_throws", "passing_bad_throw_pct",
        "times_sacked", "times_blitzed", "times_hit", "times_hurried", "times_pressured", "times_pressured_pct"
        )
).join( # Join Player IDs
    nfl.load_players().select("gsis_id", "pfr_id"),how="left", left_on = "pfr_player_id", right_on = "pfr_id"
).join( # Join Player Stats
    nfl.load_player_stats(
        seasons=seasons,
        summary_level="week"
    ).select(
        "player_id", "season", "week", "headshot_url",
        "carries", "rushing_yards", "rushing_tds",
        "rushing_fumbles","rushing_fumbles_lost", 
        "rushing_first_downs", "rushing_epa"
    ), how="left", left_on=["gsis_id", "season", "week"], right_on=["player_id", "season", "week"]
).join( # Join NextGen Stats
    nfl.load_nextgen_stats(
        seasons=seasons,
        stat_type="passing"
    ).select(
        "season", "week", "player_gsis_id", "player_short_name",
        "avg_time_to_throw", "avg_completed_air_yards", 
        "avg_intended_air_yards", "avg_air_yards_differential",
        "aggressiveness", "max_completed_air_distance", "avg_air_yards_to_sticks",
        "attempts","pass_yards","pass_touchdowns","interceptions","passer_rating",
        "completions","completion_percentage",
        "expected_completion_percentage","completion_percentage_above_expectation",
        "avg_air_distance","max_air_distance"
    ), how="left", left_on=["gsis_id", "season", "week"], right_on=["player_gsis_id", "season", "week"]
).drop_nulls()

# Fantasy Football Points Calculation
df_qb = df_qb.with_columns(
    (np.floor(df_qb["pass_yards"] / 25)).alias("ff_points_passing_yards"),
    (df_qb["pass_touchdowns"] * 4).alias("ff_points_passing_tds"),
    (df_qb["interceptions"] * (-2)).alias("ff_points_interceptions"),
    (np.floor(df_qb["rushing_yards"] / 10)).alias("ff_points_rushing_yards"),
    (df_qb["rushing_tds"] * 6).alias("ff_points_rushing_tds"),
    (df_qb["rushing_fumbles_lost"] * (-2)).alias("ff_points_rushing_fumbles_lost")
)

# Total Fantasy Football Points Calculation
df_qb = df_qb.with_columns(
    (df_qb["ff_points_passing_yards"] + 
     df_qb["ff_points_passing_tds"] + 
     df_qb["ff_points_interceptions"] +
     df_qb["ff_points_rushing_yards"] +
     df_qb["ff_points_rushing_tds"] + 
     df_qb["ff_points_rushing_fumbles_lost"]).alias("ff_points_total")
)

print(df_qb)
df_qb.write_csv("data/raw/qb_dataset.csv", decimal_comma=True, separator=";")