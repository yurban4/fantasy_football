import polars as pl
from .rolling.fantasy import add_fantasy_rolling
from .metrics.red_zone import add_red_zone_metrics
from .metrics.epa import add_expected_fantasy_points
from .utils.validation import ensure_columns

class FeatureBuilder:
    def __init__(self):
        self.df = None

    def load(self, seasons):
        from .loaders.load_player_stats import load_player_stats
        self.df = load_player_stats(seasons)
        return self

    def add_fantasy_rolling(self):
        self.df = add_fantasy_rolling(self.df)
        return self

    def add_expected_fantasy_points(self):
        self.df = add_expected_fantasy_points(self.df)
        return self

    def add_position_encoding(self):
        ensure_columns(self.df, ["position_group"])
        self.df = self.df.with_columns([
            pl.col("position_group").cast(pl.Categorical)
        ])
        return self

    def merge_pbp(self, pbp_player_df: pl.DataFrame):
        self.df = self.df.join(pbp_player_df, on="player_id", how="left")
        return self

    def build(self):
        return self.df
