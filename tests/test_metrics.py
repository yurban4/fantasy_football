from Package_NFL_ML.metrics.success import add_success_metrics
from Package_NFL_ML.metrics.epa import add_epa
from Package_NFL_ML.metrics.proe import add_proe
from Package_NFL_ML.metrics.pace import add_pace
import polars as pl


def test_success_metric(mock_pbp_df):
    df = add_success_metrics(mock_pbp_df)
    assert "success" in df.columns


def test_epa_metric(mock_pbp_df):
    df = add_epa(mock_pbp_df)
    assert "epa" in df.columns


def test_proe_metric(mock_pbp_df):
    df = add_proe(mock_pbp_df)
    assert "proe" in df.columns


def test_pace_metric(mock_pbp_df):
    df = add_pace(mock_pbp_df)
    assert "pace" in df.columns
