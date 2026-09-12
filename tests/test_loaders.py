import polars as pl
from Package_NFL_ML.loaders.load_player_stats import load_player_stats
from Package_NFL_ML.loaders.load_pbp import load_pbp_for_season


def test_load_player_stats(monkeypatch):
    monkeypatch.setattr(
        "nfl_data_py.import_weekly_data",
        lambda seasons: {"player_id": ["A"], "fantasy_points": [10]}
    )

    df = load_player_stats([2025])
    assert isinstance(df, pl.DataFrame)
    assert "player_id" in df.columns


def test_load_pbp(monkeypatch):
    monkeypatch.setattr(
        "nfl_data_py.import_pbp_data",
        lambda seasons: {"epa": [0.5], "down": [1]}
    )

    df = load_pbp_for_season(2025)
    assert isinstance(df, pl.DataFrame)
    assert "epa" in df.columns
