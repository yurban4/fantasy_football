from Package_NFL_ML import PlayByPlayBuilder


def test_pbp_builder_pipeline(mock_pbp_df, monkeypatch):
    monkeypatch.setattr(
        "Package_NFL_ML.loaders.load_pbp.load_pbp_for_season",
        lambda season: mock_pbp_df
    )

    pbp = (
        PlayByPlayBuilder()
        .load(seasons=2025)
        .add_epa()
        .add_success()
        .add_proe()
        .add_pressure()
        .add_coverage()
        .add_box_advantage()
        .add_motion()
        .add_pace()
        .aggregate_player_level()
    )

    assert "epa_mean" in pbp.player_df.columns
    assert "success_rate" in pbp.player_df.columns
