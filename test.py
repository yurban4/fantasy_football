import polars as pl
import nflreadpy as nfl

plays = nfl.load_pbp(2026).filter(pl.col("week") == 4).filter(pl.col("posteam").is_not_null())  # Beispiel

# Red Zone Plays
rz_plays = plays.filter(pl.col("yardline_100") <= 20)

metrics = {}

# 1) Red Zone Defense Efficiency
rz_def = (
    rz_plays
    .filter(pl.col("touchdown") == 1)
    .group_by("defteam")
    .count()
    .rename({"count": "rz_td_allowed"})
)

rz_drives = (
    rz_plays
    .group_by("defteam")
    .agg(pl.n_unique("drive").alias("rz_drives"))
)

metrics["red_zone_def_eff"] = (
    rz_def.join(rz_drives, on="defteam")
    .with_columns((1 - pl.col("rz_td_allowed") / pl.col("rz_drives")).alias("rz_def_eff"))
)

# 2) Red Zone Offense TD Rate
metrics["red_zone_off_td_rate"] = (
    rz_plays
    .group_by("posteam")
    .agg([
        pl.sum("touchdown").alias("rz_td"),
        pl.n_unique("drive").alias("rz_drives")
    ])
    .with_columns((pl.col("rz_td") / pl.col("rz_drives")).alias("rz_td_rate"))
)

# 3) EPA per Play
metrics["epa_per_play"] = (
    plays.group_by("posteam").agg(pl.mean("epa").alias("epa_per_play"))
)

# 4) Success Rate
metrics["success_rate"] = (
    plays
    .with_columns((pl.col("epa") > 0).alias("success"))
    .group_by("posteam")
    .agg(pl.mean("success").alias("success_rate"))
)

# 5) Third Down Conversion
metrics["third_down_conv"] = (
    plays.filter(pl.col("down") == 3)
    .group_by("posteam")
    .agg(pl.mean("first_down").alias("third_down_conv"))
)

# 6) Explosive Play Rate
metrics["explosive_rate"] = (
    plays
    .with_columns(
        ((pl.col("yards_gained") >= 10) & (pl.col("rush_attempt") == 1) |
         (pl.col("yards_gained") >= 20) & (pl.col("pass_attempt") == 1)).alias("explosive")
    )
    .group_by("posteam")
    .agg(pl.mean("explosive").alias("explosive_rate"))
)

# 7) Yards per Drive
metrics["yards_per_drive"] = (
    plays.group_by(["posteam", "drive"])
    .agg(pl.sum("yards_gained").alias("drive_yards"))
    .group_by("posteam")
    .agg(pl.mean("drive_yards").alias("yards_per_drive"))
)

# 8) Score Probability per Drive
metrics["score_prob_per_drive"] = (
    plays
    .group_by(["posteam", "drive"])
    .agg(
        pl.col("drive_ended_with_score").max().alias("scored")
    )
    .group_by("posteam")
    .agg(
        pl.mean("scored").alias("score_prob_per_drive")
    )
)



# 9) Turnover Rate
metrics["turnover_rate"] = (
    plays
    .with_columns(
        ((pl.col("interception") == 1) |
         (pl.col("fumble_lost") == 1)).alias("turnover")
    )
    .group_by(["posteam", "drive"])
    .agg(pl.max("turnover").alias("turnover"))
    .group_by("posteam")
    .agg(pl.mean("turnover").alias("turnover_rate"))
)

# 10) Pressure Rate
metrics["pressure_rate"] = (
    plays
    .with_columns(
        ((pl.col("qb_hit") == 1) | (pl.col("sack") == 1)).alias("pressure")
    )
    .filter(pl.col("pass") == 1)
    .group_by("defteam")
    .agg(pl.mean("pressure").alias("pressure_rate"))
)

print(metrics)
