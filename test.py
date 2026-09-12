from Package_NFL_ML import FeatureBuilder

pbp = (
    PlayByPlayBuilder()
    .load(seasons=[2024, 2025])
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

df = (
    FeatureBuilder()
    .load(seasons=2025)
    .add_fantasy_rolling()
    .add_expected_fantasy_points()
    .add_position_encoding()
    .merge_pbp(pbp.player_df)   # <-- jetzt korrekt!
    .build()
)
print(df)