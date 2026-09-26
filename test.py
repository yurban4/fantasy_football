import nflreadpy as nfl
import polars as pl
import numpy as np

seasons = [2022, 2023,2024, 2025,2026]

df = nfl.load_pfr_advstats(
        seasons=seasons,
        stat_type="def",
        summary_level="week"
    )

print(df.columns)