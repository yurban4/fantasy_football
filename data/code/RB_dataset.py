import nflreadpy as nfl
import polars as pl
import numpy as np
seasons = [2022, 2023, 2024, 2025, 2026]

df_rb = (
    nfl.load_pfr_advstats( # PFR Receiving Stats
        seasons=seasons,
        stat_type="rec",
        summary_level="week"
    ).select(
        "game_id", "pfr_game_id", "season", "week", "game_type", 
        "team", "opponent", "pfr_player_name", "pfr_player_id",
        "receiving_broken_tackles",  
        "receiving_drop", "receiving_drop_pct", "receiving_int", "receiving_rat"
    )
).join( # Join Player IDs
    nfl.load_players().filter(pl.col('position') == 'RB').select("gsis_id", "pfr_id", "position"),
    how="inner", left_on = "pfr_player_id", right_on = "pfr_id"
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
        "target_share", "air_yards_share", "wopr", "special_teams_tds",
        "carries", "rushing_yards", "rushing_fumbles", "rushing_fumbles_lost",
        "rushing_first_downs", "rushing_epa", "rushing_2pt_conversions",
    ), how="left", left_on=["gsis_id", "season", "week"], right_on=["player_id", "season", "week"]
).join( # Join Running Stats
    nfl.load_pfr_advstats( # PFR Receiving Stats
            seasons=seasons,
            stat_type="rush",
            summary_level="week"
    ).select(
        'season', 'week', 'game_type', 'team', 'opponent', 'pfr_player_id',
        'carries', 'rushing_yards_before_contact', 'rushing_yards_before_contact_avg', 'rushing_yards_after_contact', 
        'rushing_yards_after_contact_avg', 'rushing_broken_tackles',
    ), how="left", left_on=["pfr_player_id", "season", "week"], right_on=["pfr_player_id", "season", "week"]
)

# Fantasy Football Points Calculation
df_rb = df_rb.with_columns(
    (np.floor(df_rb["receiving_yards"] / 25)).alias("ff_points_receiving_yards"),
    (df_rb["receiving_tds"] * 6).alias("ff_points_receiving_tds"),
    (np.floor(df_rb["rushing_yards"] / 10)).alias("ff_points_rushing_yards"),
    (df_rb["rushing_tds"] * 6).alias("ff_points_rushing_tds"),
    (df_rb["rushing_fumbles_lost"] * (-2)).alias("ff_points_rushing_fumbles_lost")
)

# Total Fantasy Football Points Calculation
df_rb = df_rb.with_columns(
    (df_rb["ff_points_receiving_yards"] + 
     df_rb["ff_points_receiving_tds"] +
     df_rb["ff_points_rushing_yards"] +
     df_rb["ff_points_rushing_tds"] +
     df_rb["ff_points_rushing_fumbles_lost"]).alias("ff_total_points")
)

print(df_rb.head())
df_rb.write_csv("data/raw/rb_dataset.csv", separator=";", decimal_comma=True)