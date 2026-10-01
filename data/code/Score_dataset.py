import nflreadpy as nfl
import polars as pl
import numpy as np

seasons = [2022, 2023,2024, 2025,2026]

import polars as pl
import nflreadpy as nfl

def build_team_game_table(seasons):
    sched = nfl.load_schedules(seasons=seasons)

    # Heimteam-Zeilen
    home = (
        sched
        .select([
            "game_id", "season", "week",
            pl.col("home_team").alias("team"),
            pl.col("away_team").alias("opponent"),
            pl.col("home_score").alias("team_score"),
            pl.col("away_score").alias("opp_score"),
            pl.col("home_moneyline").alias("moneyline")
        ])
    )

    # Auswärtsteam-Zeilen
    away = (
        sched
        .select([
            "game_id", "season", "week",
            pl.col("away_team").alias("team"),
            pl.col("home_team").alias("opponent"),
            pl.col("away_score").alias("team_score"),
            pl.col("home_score").alias("opp_score"),
            pl.col("away_moneyline").alias("moneyline")
        ])
    )

    # Zusammenführen
    df = pl.concat([home, away], how = "vertical").sort(["season", "week", "game_id", "team"])

    return df

df_team_game = build_team_game_table(seasons)
df_team_game.write_csv("data/raw/team_game_data_2026.csv", decimal_comma=True, separator=";")