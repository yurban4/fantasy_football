import polars as pl

def add_ftn_pressure_metrics(df: pl.DataFrame) -> pl.DataFrame:
    if "pressure" not in df.columns or "dropback" not in df.columns:
        return df.with_columns([
            pl.lit(None).alias("pressure_events"),
            pl.lit(None).alias("dropbacks"),
            pl.lit(None).alias("pressure_rate")
        ])

    grouped = (
        df.group_by(["game_id", "posteam"])
          .agg([
              pl.col("pressure").sum().alias("pressure_events"),
              pl.col("dropback").sum().alias("dropbacks")
          ])
          .with_columns([
              (pl.col("pressure_events") / pl.col("dropbacks"))
              .alias("pressure_rate")
          ])
    )

    return df.join(grouped, on=["game_id", "posteam"], how="left")

def add_ftn_coverage_metrics(df: pl.DataFrame) -> pl.DataFrame:
    if "coverage" not in df.columns:
        return df.with_columns([
            pl.lit(None).alias("is_man"),
            pl.lit(None).alias("is_zone"),
            pl.lit(None).alias("is_blitz")
        ])

    return df.with_columns([
        (pl.col("coverage") == "man").alias("is_man"),
        (pl.col("coverage") == "zone").alias("is_zone"),
        (pl.col("blitz") == 1).alias("is_blitz")
    ])

def add_ftn_time_metrics(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns([
        pl.col("time_to_throw").alias("ttt"),
        pl.col("time_to_pressure").alias("ttp"),
        pl.col("pocket_time").alias("pocket_time")
    ])

def add_ftn_route_metrics(df: pl.DataFrame) -> pl.DataFrame:
    if "routes" not in df.columns or "targets" not in df.columns:
        return df.with_columns(pl.lit(None).alias("tprr"))

    return df.with_columns([
        (pl.col("targets") / pl.col("routes")).alias("tprr")
    ])

def add_ftn_run_metrics(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns([
        pl.col("box_count").alias("box"),
        pl.col("run_gap").alias("gap"),
        pl.col("run_direction").alias("run_dir")
    ])
