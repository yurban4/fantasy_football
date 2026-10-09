import nflreadpy as nfl
import polars as pl
import numpy as np

def get_def_stats(seasons=2026):
    df_match_scorings = build_team_game_table(
        seasons
    ).drop_nulls()

    df_def = (
        nfl.load_team_stats( # PFR Passing Stats
            seasons=seasons,
            summary_level="week"
        ).select(
            "game_id", "team", "week", "season",
            "def_tackles_solo", "def_tackles_with_assist", "def_tackle_assists",
            "def_tackles_for_loss", "def_tackles_for_loss_yards",
            "def_fumbles_forced", "def_sacks", "def_sack_yards",
            "def_qb_hits", 
            "def_interceptions", "def_interception_yards", "def_pass_defended",
            "def_tds", "def_safeties", "fumble_recovery_opp"
            )
    ).unique().join( # Join Opponent Scores
        df_match_scorings.select(
            "game_id", "team", "opp_score"
        ), how="left", left_on = ["game_id", "team"], right_on = ["game_id", "team"]
    )
    # Fantasy Football Points Calculation
    df_def = df_def.with_columns(
        (df_def["def_interceptions"] * 2).alias("ff_points_interceptions"),
        (df_def["def_tds"] * 6).alias("ff_points_tds"),
        (df_def["def_sacks"] * 1).alias("ff_points_sacks"),
        (df_def["def_safeties"] * 2).alias("ff_points_safeties"),
        (df_def["fumble_recovery_opp"] * 2).alias("ff_points_fumble_recovery_opp"),
        pl.when(df_def["opp_score"] <= 6).then(10)
        .when(df_def["opp_score"] <= 13).then(7)
        .when(df_def["opp_score"] <= 20).then(4)
        .when(df_def["opp_score"] <= 27).then(1)
        .when(df_def["opp_score"] <= 34).then(-1)
        .otherwise(-4)
        .alias("ff_points_opp_score"),
    )
    return df_def

def get_qb_stats(seasons=2026):
    df_qb = (
        nfl.load_player_stats(
            seasons=seasons,
            summary_level="week"
        ).select(
            "player_id", "season", "week", "headshot_url",
            "carries", "rushing_yards", "rushing_tds",
            "rushing_fumbles","rushing_fumbles_lost", 
            "rushing_first_downs", "rushing_epa"
        )
    ).join(
         nfl.load_players().select("gsis_id", "pfr_id", "football_name"),
         how="left", left_on = "player_id", right_on = "gsis_id"
    ).join( # Join NextGen Stats
        nfl.load_nextgen_stats(
            seasons=seasons,
            stat_type="passing"
        ).select(
            "season", "week", "player_gsis_id",
            "avg_time_to_throw", "avg_completed_air_yards", 
            "avg_intended_air_yards", "avg_air_yards_differential",
            "aggressiveness", "max_completed_air_distance", "avg_air_yards_to_sticks",
            "attempts","pass_yards","pass_touchdowns","interceptions","passer_rating",
            "completions","completion_percentage",
            "expected_completion_percentage","completion_percentage_above_expectation",
            "avg_air_distance","max_air_distance"
        ), how="left", left_on=["player_id", "season", "week"], right_on=["player_gsis_id", "season", "week"]
    ).drop_nulls()

    # Fantasy Football Points Calculation
    df_qb = df_qb.with_columns(
        (np.floor(df_qb["pass_yards"] / 25)).alias("ff_points_passing_yards"),
        (df_qb["pass_touchdowns"] * 4).alias("ff_points_passing_tds"),
        (df_qb["interceptions"] * (-2)).alias("ff_points_interceptions"),
        (np.floor(df_qb["rushing_yards"] / 10)).alias("ff_points_rushing_yards"),
        (df_qb["rushing_tds"] * 6).alias("ff_points_rushing_tds"),
        (df_qb["rushing_fumbles_lost"] * (-2)).alias("ff_points_rushing_fumbles_lost")
    )

    # Total Fantasy Football Points Calculation
    df_qb = df_qb.with_columns(
        (df_qb["ff_points_passing_yards"] + 
        df_qb["ff_points_passing_tds"] + 
        df_qb["ff_points_interceptions"] +
        df_qb["ff_points_rushing_yards"] +
        df_qb["ff_points_rushing_tds"] + 
        df_qb["ff_points_rushing_fumbles_lost"]).alias("ff_points_total")
    )

    return df_qb

def get_rb_stats(seasons=2026):
    df_rb = (
        nfl.load_pfr_advstats( # PFR Receiving Stats
            seasons=seasons,
            stat_type="rec",
            summary_level="week"
        ).select(
            "game_id", "pfr_game_id", "season", "week", "game_type", 
            "team", "opponent", "pfr_player_name", "pfr_player_id",
            "receiving_broken_tackles",  
            "receiving_drop", "receiving_drop_pct", "receiving_int", "receiving_rat"
        )
    ).join( # Join Player IDs
        nfl.load_players().filter(pl.col('position') == 'RB').select("gsis_id", "pfr_id", "position"),
        how="inner", left_on = "pfr_player_id", right_on = "pfr_id"
    ).join( # Join Player Stats
        nfl.load_player_stats(
            seasons=seasons,
            summary_level="week"
        ).select(
            "player_id", "season", "week", "headshot_url",
            "receiving_yards", "receiving_tds", "rushing_tds",
            "receiving_fumbles","receiving_fumbles_lost", 
            "receiving_air_yards", "receiving_yards_after_catch", 
            "receiving_epa", "receiving_2pt_conversions", "racr",
            "target_share", "air_yards_share", "wopr", "special_teams_tds",
            "carries", "rushing_yards", "rushing_fumbles", "rushing_fumbles_lost",
            "rushing_first_downs", "rushing_epa", "rushing_2pt_conversions",
        ), how="left", left_on=["gsis_id", "season", "week"], right_on=["player_id", "season", "week"]
    ).join( # Join Running Stats
        nfl.load_pfr_advstats( # PFR Receiving Stats
                seasons=seasons,
                stat_type="rush",
                summary_level="week"
        ).select(
            'season', 'week', 'game_type', 'team', 'opponent', 'pfr_player_id',
            'carries', 'rushing_yards_before_contact', 'rushing_yards_before_contact_avg', 'rushing_yards_after_contact', 
            'rushing_yards_after_contact_avg', 'rushing_broken_tackles',
        ), how="left", left_on=["pfr_player_id", "season", "week"], right_on=["pfr_player_id", "season", "week"]
    )

    # Fantasy Football Points Calculation
    df_rb = df_rb.with_columns(
        (np.floor(df_rb["receiving_yards"] / 25)).alias("ff_points_receiving_yards"),
        (df_rb["receiving_tds"] * 6).alias("ff_points_receiving_tds"),
        (np.floor(df_rb["rushing_yards"] / 10)).alias("ff_points_rushing_yards"),
        (df_rb["rushing_tds"] * 6).alias("ff_points_rushing_tds"),
        (df_rb["rushing_fumbles_lost"] * (-2)).alias("ff_points_rushing_fumbles_lost")
    )

    # Total Fantasy Football Points Calculation
    df_rb = df_rb.with_columns(
        (df_rb["ff_points_receiving_yards"] + 
        df_rb["ff_points_receiving_tds"] +
        df_rb["ff_points_rushing_yards"] +
        df_rb["ff_points_rushing_tds"] +
        df_rb["ff_points_rushing_fumbles_lost"]).alias("ff_total_points")
    )

    return df_rb

def get_wr_te_stats(seasons=2026):
    df_wr_te = (
        nfl.load_pfr_advstats( # PFR Receiving Stats
            seasons=seasons,
            stat_type="rec",
            summary_level="week"
        ).select(
            "game_id", "pfr_game_id", "season", "week", "game_type", 
            "team", "opponent", "pfr_player_name", "pfr_player_id",
            "receiving_broken_tackles", 
            "receiving_drop", "receiving_drop_pct", "receiving_int", "receiving_rat"
        )
    ).join( # Join Player IDs
        nfl.load_players().select("gsis_id", "pfr_id", "position").filter(pl.col('position').is_in(['WR', 'TE'])),
        how="inner", left_on = "pfr_player_id", right_on = "pfr_id"
    ).join(
        nfl.load_nextgen_stats(
            seasons=seasons,
            stat_type = "receiving"
        ).select(
            'season', 'season_type', 'week',
            'player_display_name', 'player_position', 'team_abbr', 'player_gsis_id',
            'avg_cushion', 'avg_separation', 'avg_intended_air_yards', 'percent_share_of_intended_air_yards', 
            'receptions', 'targets', 'catch_percentage', 'yards', 'rec_touchdowns', 'avg_yac', 'avg_expected_yac',
            'avg_yac_above_expectation'), 
            how="left", left_on=["gsis_id", "season", "week"], right_on=["player_gsis_id", "season", "week"]
    ).join( # Join Player Stats
        nfl.load_player_stats(
            seasons=seasons,
            summary_level="week"
        ).select(
            "player_id", "season", "week", "headshot_url",
            "receiving_yards", "receiving_tds", "rushing_tds",
            "receiving_fumbles","receiving_fumbles_lost", 
            "receiving_air_yards", "receiving_yards_after_catch", 
            "receiving_epa", "receiving_2pt_conversions", "racr",
            "target_share", "air_yards_share", "wopr", "special_teams_tds"
        ), how="left", left_on=["gsis_id", "season", "week"], right_on=["player_id", "season", "week"]
    )

    df_wr_te = df_wr_te.with_columns(
        (np.floor(df_wr_te["receiving_yards"] / 10)).alias("ff_points_receiving_yards"),
        (df_wr_te["receiving_tds"] * 6).alias("ff_points_receiving_tds"),
        (df_wr_te["receiving_fumbles_lost"] * (-2)).alias("ff_points_receiving_fumbles_lost")
    )

    df_wr_te = df_wr_te.with_columns(
        (df_wr_te["ff_points_receiving_yards"] + 
        df_wr_te["ff_points_receiving_tds"] + 
        df_wr_te["ff_points_receiving_fumbles_lost"]).alias("ff_points_total")
    )

    return df_wr_te

def build_team_game_table(seasons=2026):
    sched = nfl.load_schedules(seasons=seasons)

    # Heimteam-Zeilen
    home = (
        sched
        .select([
            "game_id", "season", "week",
            pl.col("home_team").alias("team"),
            pl.col("away_team").alias("opponent"),
            pl.col("home_score").alias("team_score"),
            pl.col("away_score").alias("opp_score"),
            pl.col("home_moneyline").alias("moneyline")
        ])
    )

    # Auswärtsteam-Zeilen
    away = (
        sched
        .select([
            "game_id", "season", "week",
            pl.col("away_team").alias("team"),
            pl.col("home_team").alias("opponent"),
            pl.col("away_score").alias("team_score"),
            pl.col("home_score").alias("opp_score"),
            pl.col("away_moneyline").alias("moneyline")
        ])
    )

    # Zusammenführen
    df = pl.concat([home, away], how = "vertical").sort(["season", "week", "game_id", "team"])

    return df

def get_kick_stats(seasons=2026):
    df_kick = (
        nfl.load_team_stats( 
            seasons=seasons,
            summary_level="week"
        ).select(
            "game_id", "team", "week", "season",
            "passing_2pt_conversions", "rushing_2pt_conversions",
        )
    ).join( # Join Player Stats
        nfl.load_player_stats(
            seasons=seasons,
            summary_level="week"
        ).select(
            "player_id", "season", "week", "team",
            "fg_made", "fg_missed", "fg_att", "fg_blocked",
            "fg_made_0_19", "fg_made_20_29", "fg_made_30_39",
            "fg_made_40_49", "fg_made_50_59", "fg_made_60_",
            "fg_missed_0_19", "fg_missed_20_29", "fg_missed_30_39",
            "fg_missed_40_49", "fg_missed_50_59", "fg_missed_60_",
            "pat_att", "pat_missed", "pat_blocked", "pat_pct", 'pat_made',
            "gwfg_made", "gwfg_att"
        ), how="left", left_on=["team", "season", "week"], right_on=["team", "season", "week"]
    ).join(
        nfl.load_players().select("gsis_id", "position", "headshot", 'football_name', 'short_name'),
        how="left", left_on = "player_id", right_on = "gsis_id"
    ).drop_nulls()

    # Fantasy Football Points Calculation
    df_kick = df_kick.with_columns(
        (df_kick["pat_made"] * 1).alias("ff_points_pat"),
        ((df_kick["fg_made_0_19"] + df_kick["fg_made_20_29"] + df_kick["fg_made_30_39"]) * 3 ).alias("ff_points_fg_0_39"),
        (df_kick["fg_made_40_49"] * 4).alias("ff_points_fg_40_49"),
        ((df_kick["fg_made_50_59"] + df_kick["fg_made_60_"]) * 5).alias("ff_points_fg_50_")
    )
    df_kick = df_kick.with_columns(
        (df_kick["ff_points_pat"] +  df_kick["ff_points_fg_0_39"] + df_kick["ff_points_fg_40_49"] + df_kick["ff_points_fg_50_"]).alias("ff_points_total"),
    )

    return df_kick

get_def_stats()
get_qb_stats()