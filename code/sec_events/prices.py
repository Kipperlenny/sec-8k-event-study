"""Price sources. The dataset ships no prices: bring your own series of adjusted closes.

Every loader returns ``dict[ticker, pd.Series]`` with a DatetimeIndex (ascending, one row
per session) and float closes. Adjusted closes (dividends and splits folded in) are what
our benchmark tables were computed from; use the same kind or expect small differences.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

BENCHMARK_CANDIDATES = ("URTH", "ACWI", "SPY")  # MSCI World ETF, spliced with ACWI / S&P 500 before it existed


def _clean(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").dropna()
    s.index = pd.to_datetime(s.index)
    s = s[~s.index.duplicated(keep="last")].sort_index()
    s.name = "close"
    return s.astype(float)


def load_prices_csv_dir(directory: str | Path, tickers: Iterable[str], date_col: str = "date", close_col: str = "close") -> dict[str, pd.Series]:
    """Read <directory>/<TICKER>.csv files with a date and a close column. Missing files are skipped
    (the study reports them as no_price_data)."""
    out: dict[str, pd.Series] = {}
    for t in tickers:
        p = Path(directory) / f"{t}.csv"
        if p.is_file():
            df = pd.read_csv(p)
            out[t] = _clean(pd.Series(df[close_col].to_numpy(), index=df[date_col]))
    return out


def load_prices_yfinance(tickers: Iterable[str], start: str = "1990-01-01", batch: int = 100) -> dict[str, pd.Series]:
    """Adjusted closes from Yahoo Finance via the yfinance package (pip install yfinance).

    Yahoo's terms allow personal use only; check them, or use a licensed vendor, before any
    commercial use of the prices themselves. Tickers Yahoo does not know are skipped.
    """
    import yfinance as yf  # optional dependency

    tickers = sorted(set(tickers))
    out: dict[str, pd.Series] = {}
    for i in range(0, len(tickers), batch):
        chunk = tickers[i:i + batch]
        data = yf.download(chunk, start=start, auto_adjust=True, progress=False, group_by="ticker", threads=True)
        if data is None or data.empty:
            continue
        for t in chunk:
            try:
                s = data[t]["Close"] if isinstance(data.columns, pd.MultiIndex) else data["Close"]
            except KeyError:
                continue
            s = _clean(s)
            if len(s) > 1:
                out[t] = s
    return out


def spliced_benchmark(prices: dict[str, pd.Series], candidates: Iterable[str] = BENCHMARK_CANDIDATES) -> tuple[str, pd.Series | None]:
    """One continuous benchmark index from candidates in priority order (same rule as our run):
    each day uses the daily return of the highest-priority candidate that has data that day.
    Returns (symbol like 'URTH+ACWI+SPY', price-like series starting at 100)."""
    available = [(c, prices[c]) for c in candidates if c in prices and not prices[c].empty]
    if not available:
        return "", None
    calendar = available[0][1].index
    for _, s in available[1:]:
        calendar = calendar.union(s.index)
    daily = pd.Series(np.nan, index=calendar.sort_values())
    for _, s in reversed(available):
        rets = s.pct_change()
        daily.loc[rets.index[1:]] = rets.iloc[1:].to_numpy()
        if np.isnan(daily.loc[rets.index[0]]):
            daily.loc[rets.index[0]] = 0.0
    daily = daily.dropna()
    index = 100.0 * (1.0 + daily).cumprod()
    index.name = "close"
    return "+".join(c for c, _ in available), index
