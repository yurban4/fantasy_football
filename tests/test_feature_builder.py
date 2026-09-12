from Package_NFL_ML import FeatureBuilder


def test_feature_builder_pipeline(mock_player_df, monkeypatch):
    # Mock loader
    monkeypatch.setattr(
        "Package_NFL_ML.loaders.load_player_stats.load_player_stats",
        lambda seasons: mock_player_df
    )

    fb = (
        FeatureBuilder()
        .load(seasons=2025)
        .add_fantasy_rolling()
        .add_expected_fantasy_points()
        .add_position_encoding()
        .build()
    )

    assert "fantasy_points_rollmean_3" in fb.columns
    assert fb["position_group"].dtype == fb["position_group"].dtype
