import polars as pl
import nflreadpy as nfl

def load_player_stats(seasons):
    if isinstance(seasons, int):
        seasons = [seasons]

    df = nfl.load_player_stats(seasons, summary_level='week')
    return df
