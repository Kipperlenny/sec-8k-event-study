"""Load the event tables and the shipped benchmark tables with schema checks."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

# The ZIP unpacks to <root>/{data,code,docs}; the package lives in <root>/code/sec_events.
# Override with SEC_EVENTS_DATA=/path/to/data when you move things around.
DATA_DIR = Path(os.environ.get("SEC_EVENTS_DATA", Path(__file__).resolve().parents[2] / "data"))

EVENT_COLUMNS = {                 # required columns and their dtypes (see docs/DATA_DICTIONARY.md)
    "event_id": "string",           # <item>-<accession_no>, stable across versions
    "event_class": "string",        # e.g. item_2_05_restructuring
    "item": "string",               # the 8-K item that defines the class, e.g. 2.05
    "form_type": "string",          # 8-K or 8-K/A
    "ticker": "string",             # ticker EDGAR lists for the CIK (see ticker_mapping)
    "company": "string",            # filer name as listed by EDGAR
    "cik": "Int64",                 # SEC Central Index Key
    "accession_no": "string",       # EDGAR accession number, 0000000000-00-000000
    "filing_date": "datetime64[ns]",
    "index_name": "string",         # SP500 or NASDAQ100
    "point_in_time": "boolean",     # True: membership checked at the filing date; False: current members list
    "items_in_filing": "string",    # all 8-K items in that filing, comma separated
    "source_url": "string",         # the filing's folder on sec.gov
    "confidence": "float64",        # 1.0 = defined by the 8-K item itself
}
OPTIONAL_COLUMNS = {              # present in v1; coerced when there, not required (your own event table needs only the above)
    "in_benchmark_run": "boolean",  # True: one of the events the shipped aggregates were computed from
    "accepted_at_et": "string",     # EDGAR acceptance datetime, US Eastern, ISO 8601 ("" if unknown)
    "event_session": "string",      # pre_market / market_hours / after_market / non_trading_day / unknown
    "first_full_session": "string", # first US session that opens after acceptance
    "benchmark_entry_date": "string",  # entry session used by the shipped aggregates (filing session + 1)
    "period_of_report": "string", "sic_code": "string", "state_of_inc": "string",
    "ticker_mapping": "string", "rule_version": "string",
}


def _events_dir() -> Path:
    return DATA_DIR / "events"


def list_event_classes() -> list[str]:
    """Names of the shipped event classes (one CSV each under data/events/)."""
    return sorted(p.stem for p in _events_dir().glob("*.csv"))


def validate_events(df: pd.DataFrame) -> pd.DataFrame:
    """Check the schema, coerce dtypes, and return a copy sorted by ticker and date.

    Raises ValueError with the first problem found. Used by load_events and by the tests.
    """
    missing = [c for c in EVENT_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"event table lacks columns: {missing}")
    out = df.copy()
    for col, dtype in {**EVENT_COLUMNS, **{c: d for c, d in OPTIONAL_COLUMNS.items() if c in out.columns}}.items():
        if dtype.startswith("datetime"):
            out[col] = pd.to_datetime(out[col], errors="raise")
        elif dtype == "string":
            out[col] = out[col].fillna("").astype(dtype)
        else:
            out[col] = out[col].astype(dtype)
    if out["filing_date"].isna().any():
        raise ValueError("filing_date has empty values")
    if (out["ticker"].str.len() == 0).any():
        raise ValueError("ticker has empty values")
    dup = out.duplicated(["event_class", "ticker", "filing_date"])
    if dup.any():
        raise ValueError(f"{int(dup.sum())} duplicate (event_class, ticker, filing_date) rows")
    if not out["accession_no"].str.fullmatch(r"\d{10}-\d{2}-\d{6}").all():
        raise ValueError("accession_no must look like 0000000000-00-000000")
    return out.sort_values(["ticker", "filing_date"]).reset_index(drop=True)


def load_events(event_class: str | Path, benchmark_subset: bool = False) -> pd.DataFrame:
    """Load one event class by name (see list_event_classes) or from a CSV path.

    The returned frame also carries the two column names the study engine uses
    (`event_date` = filing_date, `event_type` = event_class), so it can be passed
    to run_event_study directly.

    ``benchmark_subset=True`` keeps only the rows the shipped aggregates were computed from
    (`in_benchmark_run`). Use it whenever you want to reproduce `data/benchmarks/<class>/summary.csv`:
    for Item 2.05 the file also carries 20 NASDAQ-100 events that our run did not include.
    """
    path = Path(event_class) if str(event_class).endswith(".csv") else _events_dir() / f"{event_class}.csv"
    if not path.is_file():
        raise FileNotFoundError(f"{path} (known classes: {list_event_classes()})")
    df = validate_events(pd.read_csv(path, dtype={"cik": "Int64", "accession_no": str}))
    if benchmark_subset and "in_benchmark_run" in df.columns:
        df = df[df["in_benchmark_run"].fillna(True).astype(bool)].reset_index(drop=True)
    df["event_date"] = df["filing_date"]
    df["event_type"] = df["event_class"]
    return df


def load_table(event_class: str, name: str) -> pd.DataFrame | dict:
    """A shipped benchmark table for an event class: 'summary', 'breakdown_by_year',
    'breakdown_by_index', 'breakdown_by_regime', 'calendar_time_1y' (CSV -> DataFrame),
    or 'verdict' / 'run' (JSON -> dict)."""
    d = DATA_DIR / "benchmarks" / event_class
    for ext in ("csv", "json"):
        p = d / f"{name}.{ext}"
        if p.is_file():
            return pd.read_csv(p) if ext == "csv" else json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"no {name}.csv/json under {d}")


def load_summary(event_class: str) -> pd.DataFrame:
    """The shipped per-horizon summary (our run) for an event class."""
    return load_table(event_class, "summary")
