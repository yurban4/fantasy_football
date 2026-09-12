import nflreadpy as nfl
import polars as pl
from jinja2 import Environment, FileSystemLoader

# ---------------------------------------------------------
# 1) Zufälliges Spiel laden
# ---------------------------------------------------------

random_game = nfl.load_schedules(2024).sample(
    n=1, with_replacement=False, shuffle=True, seed=42
).select([
    "game_id", "home_team", "away_team",
    "home_score", "away_score"
])

game_id = random_game["game_id"][0]
home = random_game["home_team"][0]
away = random_game["away_team"][0]

print(f"📘 Spiel geladen: {away} @ {home} (game_id={game_id})")

# ---------------------------------------------------------
# 2) Play-by-Play + FTN Charting laden
# ---------------------------------------------------------

pbp = nfl.load_pbp(2024)
chart = nfl.load_ftn_charting(2024).with_columns(
    pl.col("nflverse_play_id").cast(pl.Float64)
)

random_game_detailed = (
    random_game[["game_id"]]
    .join(pbp, on="game_id", how="left")
    .join(
        chart,
        left_on=["game_id", "play_id"],
        right_on=["nflverse_game_id", "nflverse_play_id"],
        how="left"
    )
    .filter(pl.col("play_type").is_not_null())
)

# ---------------------------------------------------------
# 3) Relevante Spalten auswählen
# ---------------------------------------------------------

random_game_detailed = random_game_detailed.select([
    "desc", "posteam",
    "quarter_seconds_remaining", "half_seconds_remaining", "qtr",
    "drive", "drive_end_transition",
    "down", "goal_to_go", "ydstogo", "play_type", "success",
    "yardline_100",
    "wp", "wpa",
    "timeout_team", "posteam_timeouts_remaining", "defteam_timeouts_remaining",
    "posteam_score", "defteam_score", "score_differential",
    "no_score_prob", "touchdown", "return_touchdown", "td_prob", "fg_prob",
    "first_down_rush", "first_down_pass", "first_down_penalty",
    "third_down_converted", "third_down_failed",
    "fourth_down_converted", "fourth_down_failed",
    "fumble_forced", "fumble_not_forced",
    "rush_attempt", "pass_attempt", "sack",
    "return_team",
    "kick_distance", "extra_point_result", "two_point_conv_result",
    "n_offense_backfield", "n_defense_box", "is_motion", "n_pass_rushers", "n_blitzers",
    "is_rpo", "is_screen_pass", "is_trick_play", "is_play_action", "is_throw_away",
    "is_catchable_ball", "is_contested_ball", "is_drop",
    "is_interception_worthy",
    "is_qb_sneak"
])

# ---------------------------------------------------------
# 4) Live-Spielstand pro Play berechnen
# ---------------------------------------------------------

random_game_detailed = random_game_detailed.with_columns([
    pl.when(pl.col("posteam") == home)
      .then(pl.col("posteam_score"))
      .otherwise(pl.col("defteam_score"))
      .alias("home_score_live").cast(pl.Int16),

    pl.when(pl.col("posteam") == away)
      .then(pl.col("posteam_score"))
      .otherwise(pl.col("defteam_score"))
      .alias("away_score_live").cast(pl.Int16)
])

# ---------------------------------------------------------
# 5) Team-Logos + Farben laden
# ---------------------------------------------------------

teams = nfl.load_teams()

home_logo = teams.filter(pl.col("team_abbr") == home).select("team_logo_espn").item()
away_logo = teams.filter(pl.col("team_abbr") == away).select("team_logo_espn").item()

home_color = teams.filter(pl.col("team_abbr") == home).select("team_color").item()
away_color = teams.filter(pl.col("team_abbr") == away).select("team_color").item()

# ---------------------------------------------------------
# 6) Jinja2 Template laden
# ---------------------------------------------------------

env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=False
)

template = env.get_template("play_by_play.html")

# ---------------------------------------------------------
# 7) Rendern
# ---------------------------------------------------------

output = template.render(
    plays=random_game_detailed.to_dicts(),
    home_team=home,
    away_team=away,
    home_score=random_game["home_score"][0],
    away_score=random_game["away_score"][0],
    home_logo=home_logo,
    away_logo=away_logo,
    home_color=home_color,
    away_color=away_color
)

# ---------------------------------------------------------
# 8) HTML speichern
# ---------------------------------------------------------

with open("report.html", "w", encoding="utf-8") as f:
    f.write(output)

print("✅ HTML-Report erstellt: report.html")