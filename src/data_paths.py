"""Default path to the airlines flights CSV (repo root preferred)."""

from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent

_ROOT_CSV = _REPO_ROOT / "airlines_flights_data.csv"
_RAW_CSV = _REPO_ROOT / "data" / "raw" / "airlines_flights_data.csv"


def resolve_data_path(explicit: Optional[str] = None) -> str:
    """Return dataset path: explicit arg, else root CSV, else legacy data/raw path."""
    if explicit:
        return explicit
    if _ROOT_CSV.exists():
        return str(_ROOT_CSV)
    if _RAW_CSV.exists():
        return str(_RAW_CSV)
    return str(_ROOT_CSV)
