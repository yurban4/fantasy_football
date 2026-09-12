import polars as pl
import nflreadpy as nfl

def load_rosters(seasons):
    df = nfl.load_rosters(seasons)
    return df
