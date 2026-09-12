from Package_NFL_ML.rolling.fantasy import add_fantasy_rolling


def test_fantasy_rolling(mock_player_df):
    df = add_fantasy_rolling(mock_player_df)
    assert "fantasy_points_rollmean_3" in df.columns
    assert "fantasy_points_rollsum_3" in df.columns
