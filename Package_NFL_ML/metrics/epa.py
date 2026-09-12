import polars as pl

def add_epa(df: pl.DataFrame) -> pl.DataFrame:
    """
    Stellt sicher, dass eine EPA-Spalte existiert.
    Falls keine vorhanden ist, wird sie mit None gefüllt.
    """
    if "epa" not in df.columns:
        return df.with_columns(pl.lit(None).alias("epa"))
    return df


def add_expected_fantasy_points(df: pl.DataFrame) -> pl.DataFrame:
    """
    Beispielhafte Expected Fantasy Points Berechnung.
    Du kannst später deine echte Formel einbauen.
    """
    # Falls die Spalten nicht existieren, mit 0 füllen
    df = df.with_columns([
        pl.col("targets").fill_null(0),
        pl.col("carries").fill_null(0),
        pl.col("red_zone_touches").fill_null(0)
    ])

    return df.with_columns([
        (
            pl.col("targets") * 0.7 +
            pl.col("carries") * 0.3 +
            pl.col("red_zone_touches") * 1.2
        ).alias("expected_fantasy_points")
    ])
