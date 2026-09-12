import polars as pl

from Package_NFL_ML.loaders.load_ftn_chart import load_ftn_charting
from Package_NFL_ML.metrics.ftn_metrics import add_ftn_run_metrics
from .loaders.load_pbp import load_pbp_for_season
from .metrics.epa import add_epa
from .metrics.success import add_success_metrics
from .metrics.proe import add_proe
from .metrics.pressure import add_pressure_metrics
from .metrics.coverage import add_coverage_metrics
from .metrics.box_advantage import add_box_advantage
from .metrics.pace import add_pace
from .metrics.motion import add_play_action_motion
from Package_NFL_ML.loaders.join_ftn_charting_to_pbp import join_ftn_charting_to_pbp
from Package_NFL_ML.metrics.ftn_metrics import (
    add_ftn_pressure_metrics,
    add_ftn_coverage_metrics,
    add_ftn_time_metrics,
    add_ftn_route_metrics,
    add_ftn_run_metrics
)


class PlayByPlayBuilder:
    def __init__(self):
        self.df = None
        self.player_df = None

    def load(self, seasons):
        pbp = load_pbp_for_season(seasons)
        ftn = load_ftn_charting(seasons)

        pbp = join_ftn_charting_to_pbp(pbp, ftn)
        print(f"pbp.columns: {pbp.columns}")
        pbp = add_ftn_pressure_metrics(pbp)
        pbp = add_ftn_coverage_metrics(pbp)
        pbp = add_ftn_time_metrics(pbp)
        pbp = add_ftn_route_metrics(pbp)
        pbp = add_ftn_run_metrics(pbp)

        self.df = pbp
        return self

    def add_epa(self):
        self.df = add_epa(self.df)
        return self

    def add_success(self):
        self.df = add_success_metrics(self.df)
        return self

    def add_proe(self):
        self.df = add_proe(self.df)
        return self

    def add_pressure(self):
        self.df = add_pressure_metrics(self.df)
        return self

    def add_coverage(self):
        self.df = add_coverage_metrics(self.df)
        return self

    def add_box_advantage(self):
        self.df = add_box_advantage(self.df)
        return self

    def add_motion(self):
        self.df = add_play_action_motion(self.df)
        return self

    def add_pace(self):
        self.df = add_pace(self.df)
        return self

    def aggregate_player_level(self):
        self.player_df = (
            self.df.group_by("player_id")
            .agg([
                pl.col("epa").mean().alias("epa_mean"),
                pl.col("success").mean().alias("success_rate"),
                pl.col("pressure").mean().alias("pressure_rate"),
            ])
        )
        return self
    
    def join_ftn_charting_to_pbp(pbp: pl.DataFrame, ftn: pl.DataFrame) -> pl.DataFrame:
        """
        Joint FTN-Charting-Daten robust an die PBP-Tabelle.
        Erwartet gemeinsame Keys:
        - game_id
        - play_id
        """

        pbp = pbp.rename({c: c.lower() for c in pbp.columns})
        ftn = ftn.rename({c: c.lower() for c in ftn.columns})

        required = ["game_id", "play_id"]
        for col in required:
            if col not in pbp.columns or col not in ftn.columns:
                raise ValueError(f"Missing join key: {col}")

        return pbp.join(ftn, on=["game_id", "play_id"], how="left")

    def build(self):
        return self.df
