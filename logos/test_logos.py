import requests
from pathlib import Path
import nflreadpy as nfl

def download_team_logos():
    teams = nfl.load_teams()

    logo_dir = Path("logos")
    logo_dir.mkdir(exist_ok=True)

    for row in teams.iter_rows(named=True):
        url = row["team_logo_espn"]
        team = row["team_abbr"]

        out_path = logo_dir / f"{team}.png"

        if not out_path.exists():
            print(f"Lade Logo für {team}…")
            r = requests.get(url)
            out_path.write_bytes(r.content)

    print("Alle Logos geladen.")

download_team_logos()