"""sec_events - loader and reproducible event-study benchmark for the SEC 8-K Event Dataset.

Quick start::

    from sec_events import load_events, load_prices_yfinance, spliced_benchmark, run_event_study
    ev = load_events("item_2_06_impairment")
    prices = load_prices_yfinance(sorted(set(ev.ticker)) + ["URTH", "ACWI", "SPY"])
    bm_symbol, bm = spliced_benchmark(prices)
    res = run_event_study(ev, prices, bm, bm_symbol)
    print(res.summary[["horizon", "trades", "mean_return_pct", "mean_abnormal_return_pct"]])

The dataset ships events and our aggregate statistics. Prices are not included: you
supply them from a source whose terms allow your use (see docs/DATA_DICTIONARY.md).
"""

from .loader import DATA_DIR, list_event_classes, load_events, load_summary, load_table, validate_events
from .prices import load_prices_csv_dir, load_prices_yfinance, spliced_benchmark
from .study import StudyConfig, StudyResult, run_event_study, compare_with_shipped

__version__ = "1.0.0"
__all__ = [
    "DATA_DIR", "list_event_classes", "load_events", "load_summary", "load_table", "validate_events",
    "load_prices_csv_dir", "load_prices_yfinance", "spliced_benchmark",
    "StudyConfig", "StudyResult", "run_event_study", "compare_with_shipped",
]
