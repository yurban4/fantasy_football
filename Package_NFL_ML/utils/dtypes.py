import polars as pl

# Häufig genutzte Polars-Datentypen
DTYPE_INT = pl.Int64
DTYPE_FLOAT = pl.Float64
DTYPE_STR = pl.Utf8
DTYPE_BOOL = pl.Boolean

# Convenience-Mapping für spätere Validierungen
DTYPE_MAP = {
    "int": DTYPE_INT,
    "float": DTYPE_FLOAT,
    "str": DTYPE_STR,
    "bool": DTYPE_BOOL,
}
