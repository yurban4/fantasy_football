import polars as pl

def ensure_columns(df: pl.DataFrame, cols: list[str]):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df

def validate_columns(df: pl.DataFrame, schema: dict[str, pl.DataType]):
    """
    Prüft, ob bestimmte Spalten existieren UND den richtigen Datentyp haben.
    """
    ensure_columns(df, list(schema.keys()))

    for col, dtype in schema.items():
        if df[col].dtype != dtype:
            raise TypeError(
                f"Column '{col}' has dtype {df[col].dtype}, expected {dtype}"
            )
    return df

def validate_numeric(df: pl.DataFrame, cols: list[str]):
    """
    Prüft, ob bestimmte Spalten numerisch sind.
    """
    ensure_columns(df, cols)

    for col in cols:
        if df[col].dtype not in (pl.Int64, pl.Float64):
            raise TypeError(
                f"Column '{col}' must be numeric, got {df[col].dtype}"
            )
    return df
