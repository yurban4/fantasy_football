import pytest
from Package_NFL_ML.utils.validation import ensure_columns


def test_ensure_columns_success(mock_player_df):
    ensure_columns(mock_player_df, ["player_id"])


def test_ensure_columns_fail(mock_player_df):
    with pytest.raises(ValueError):
        ensure_columns(mock_player_df, ["does_not_exist"])
