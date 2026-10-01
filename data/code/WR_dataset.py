import nflreadpy as nfl
import polars as pl
import numpy as np
seasons = [2022, 2023, 2024, 2025, 2026]

df_wr = (
    nfl.load_pfr_advstats( # PFR Receiving Stats
        seasons=seasons,
        stat_type="rec",
        summary_level="week"
    ).select(
        "game_id", "pfr_game_id", "season", "week", "game_type", 
        "team", "opponent", "pfr_player_name", "pfr_player_id",
        "rushing_broken_tackles", "receiving_broken_tackles", "passing_drops", "passing_drop_pct", 
        "receiving_drop", "receiving_drop_pct", "receiving_int", "receiving_rat"
    )
).join( # Join Player IDs
    nfl.load_players().select("gsis_id", "pfr_id"),how="left", left_on = "pfr_player_id", right_on = "pfr_id"
).join(
    nfl.load_nextgen_stats(
        seasons=seasons,
        stat_type = "receiving"
    ).select(
        'season', 'season_type', 'week',
        'player_display_name', 'player_position', 'team_abbr', 'player_gsis_id',
        'avg_cushion', 'avg_separation', 'avg_intended_air_yards', 'percent_share_of_intended_air_yards', 
        'receptions', 'targets', 'catch_percentage', 'yards', 'rec_touchdowns', 'avg_yac', 'avg_expected_yac',
        'avg_yac_above_expectation'
    ), how="left", left_on=["gsis_id", "season", "week"], right_on=["player_gsis_id", "season", "week"]
).join( # Join Player Stats
    nfl.load_player_stats(
        seasons=seasons,
        summary_level="week"
    ).select(
        "player_id", "season", "week", "headshot_url",
        "receiving_yards", "receiving_tds", "rushing_tds",
        "receiving_fumbles","receiving_fumbles_lost", 
        "receiving_air_yards", "receiving_yards_after_catch", 
        "receiving_epa", "receiving_2pt_conversions", "racr",
        "target_share", "air_yards_share", "wopr", "special_teams_tds"
    ), how="left", left_on=["gsis_id", "season", "week"], right_on=["player_id", "season", "week"]
)

print(df_wr.head())
df_wr.write_csv("data/raw/wr_dataset.csv", separator=";", decimal_comma=True)