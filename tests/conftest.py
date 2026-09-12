import polars as pl
import pytest


@pytest.fixture
def mock_player_df():
    return pl.DataFrame({
        "player_id": ["A", "A", "B", "B"],
        "week": [1, 2, 1, 2],
        "fantasy_points": [10, 20, 5, 15],
        "position_group": ["RB", "RB", "WR", "WR"],
        "targets": [5, 7, 3, 4],
        "carries": [10, 12, 1, 2],
        "red_zone_touches": [2, 3, 1, 0]
    })


@pytest.fixture
def mock_pbp_df():
    return pl.DataFrame({
        "play_id": [1, 2, 3, 4],
        "game_id": ["G1", "G1", "G2", "G2"],
        "old_game_id": ["OG1", "OG1", "OG2", "OG2"],
        "posteam": ["KC", "KC", "BUF", "BUF"],
        "week": [1, 2, 1, 2],
        "epa": [0.5, -0.2, 0.1, 0.3],
        "down": [1, 2, 1, 3],
        "pass": [1, 0, 1, 1],
        "pressure": [0, 1, 0, 1],               # ← WICHTIG
        "coverage": ["man", "zone", "zone", "man"],
        "box": [7, 6, 5, 7],
        "time_to_snap": [28, 30, 27, 29],
        "motion": [True, False, True, False],
        "yardline_100": [15, 30, 10, 50]
    })

