"""Event-study engine: reproduces the shipped benchmark tables from the event table and your prices.

Definitions (identical to the run that produced data/benchmarks/*):

* entry  = first session on or after the filing date, plus ``entry_lag_sessions`` (default 1,
           because filings often land after the close)
* exit   = first session on or after entry + round(365.25 * horizon_years) days
* return = exit_close / entry_close - 1 minus ``stock_cost_bps`` (round trip)
* benchmark return = the spliced benchmark over exactly the same dates minus ``benchmark_cost_bps``
* abnormal return  = return - benchmark return (buy-and-hold abnormal return)
* placebo = same stock, same holding length, ``placebo_samples`` random other entry days within
            +/- ``placebo_window_years`` and at least ``placebo_exclusion_days`` away, seeded
* per horizon: mean/median, win rate, bootstrap CI of the mean (``n_bootstrap`` resamples),
  Bonferroni-adjusted CI across horizons, in-sample/out-of-sample split (first 60 % of trades
  by entry date), most recent ``recent_years``, bull/bear regime at entry (benchmark below its
  200-session average = bear), 5 % winsorized means, and a calendar-time portfolio
  (equal-weighted monthly returns of all stocks inside an active window vs the benchmark).

Bootstrap and placebo use their own seeded generator per horizon, so single numbers such as the
mean are exact given the same prices, while CI bounds and placebo means differ only within
sampling noise from the shipped tables (the original run drew from one shared stream).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np
import pandas as pd

MAX_ENTRY_GAP_DAYS = 10


@dataclass(frozen=True)
class StudyConfig:
    horizons_years: tuple[float, ...] = (0.1, 1.0, 3.0, 5.0)
    entry_lag_sessions: int = 1
    stock_cost_bps: float = 20.0
    benchmark_cost_bps: float = 5.0
    placebo_samples: int = 200
    placebo_window_years: float = 10.0
    placebo_exclusion_days: int = 30
    seed: int = 42
    confidence_level: float = 0.95
    in_sample_fraction: float = 0.6
    recent_years: float = 5.0
    regime_ma_sessions: int = 200
    n_bootstrap: int = 2000

    @classmethod
    def from_run(cls, run: Mapping[str, Any]) -> "StudyConfig":
        """Build the config from a shipped data/benchmarks/<class>/run.json."""
        ev = run.get("evaluation", {})
        return cls(
            horizons_years=tuple(float(h) for h in run["horizons_years"]),
            entry_lag_sessions=int(run.get("entry_lag_sessions", 1)),
            stock_cost_bps=float(run.get("stock_round_trip_bps", 20.0)),
            benchmark_cost_bps=float(run.get("benchmark_round_trip_bps", 5.0)),
            placebo_samples=int(ev.get("placebo_samples", 200)),
            placebo_window_years=float(ev.get("placebo_window_years", 10.0)),
            placebo_exclusion_days=int(ev.get("placebo_exclusion_days", 30)),
            seed=int(ev.get("seed", 42)),
            confidence_level=float(ev.get("confidence_level", 0.95)),
            in_sample_fraction=float(ev.get("in_sample_fraction", 0.6)),
            recent_years=float(ev.get("recent_years", 5)),
            regime_ma_sessions=int(ev.get("regime_ma_sessions", 200)),
        )


@dataclass
class StudyResult:
    trades: pd.DataFrame
    skipped: pd.DataFrame
    summary: pd.DataFrame
    breakdown_by_year: pd.DataFrame = field(default_factory=pd.DataFrame)
    breakdown_by_index: pd.DataFrame = field(default_factory=pd.DataFrame)
    breakdown_by_regime: pd.DataFrame = field(default_factory=pd.DataFrame)
    calendar_time: dict[str, pd.DataFrame] = field(default_factory=dict)
    benchmark_symbol: str = ""


# ----------------------------------------------------------------------------- helpers

def horizon_label(h: float) -> str:
    return f"{h:g}y"


def holding_days_for(h: float) -> int:
    return int(round(365.25 * h))


def _first_on_or_after(idx: pd.DatetimeIndex, day: pd.Timestamp) -> pd.Timestamp | None:
    pos = idx.searchsorted(day, side="left")
    return idx[pos] if pos < len(idx) else None


def bootstrap_mean_ci(values: np.ndarray, rng: np.random.Generator, level: float, n_boot: int) -> tuple[float, float]:
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if v.size < 2:
        return float("nan"), float("nan")
    means = rng.choice(v, size=(n_boot, v.size), replace=True).mean(axis=1)
    tail = (1.0 - level) / 2.0 * 100.0
    return float(np.percentile(means, tail)), float(np.percentile(means, 100.0 - tail))


def t_stat(values: np.ndarray) -> float:
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if v.size < 2:
        return float("nan")
    sd = v.std(ddof=1)
    return float(v.mean() / (sd / np.sqrt(v.size))) if sd > 0 else float("nan")


def winsorized_mean(values: np.ndarray, pct: float = 5.0) -> float:
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if v.size == 0:
        return float("nan")
    lo, hi = np.percentile(v, [pct, 100.0 - pct])
    return float(np.clip(v, lo, hi).mean())


def holding_period_returns(px: pd.Series, holding_days: int) -> pd.Series:
    """Return for every entry day whose exit (first session on/after entry + holding_days) exists."""
    idx = px.index
    values = px.to_numpy(dtype=float)
    exit_pos = idx.searchsorted(idx + pd.Timedelta(days=holding_days), side="left")
    valid = exit_pos < len(idx)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = values[exit_pos[valid]] / values[valid] - 1.0
    return pd.Series(r, index=idx[valid])


def placebo_returns(px: pd.Series, entry: pd.Timestamp, holding_days: int, cfg: StudyConfig, rng: np.random.Generator,
                    cache: dict[int, pd.Series]) -> np.ndarray:
    all_r = cache.get(holding_days)
    if all_r is None:
        all_r = cache[holding_days] = holding_period_returns(px, holding_days)
    if all_r.empty:
        return np.array([], dtype=float)
    dist = np.abs((all_r.index - entry).days)
    mask = (dist <= int(round(cfg.placebo_window_years * 365.25))) & (dist >= cfg.placebo_exclusion_days)
    cand = all_r.to_numpy(dtype=float)[mask]
    if cand.size <= cfg.placebo_samples:
        return cand
    return cand[np.sort(rng.choice(cand.size, size=cfg.placebo_samples, replace=False))]


# ----------------------------------------------------------------------------- trades

def build_trades(events: pd.DataFrame, prices: Mapping[str, pd.Series], benchmark: pd.Series | None, benchmark_symbol: str,
                 cfg: StudyConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(cfg.seed)
    stock_cost, bench_cost = cfg.stock_cost_bps / 1e4, cfg.benchmark_cost_bps / 1e4
    bear = None
    if benchmark is not None and len(benchmark) > cfg.regime_ma_sessions:
        bear = benchmark < benchmark.rolling(cfg.regime_ma_sessions).mean()
    trades: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    plan = [(horizon_label(h), h) for h in cfg.horizons_years]

    def skip(row: Any, label: str, reason: str) -> None:
        skipped.append({"ticker": str(row.ticker), "event_date": row.event_date, "horizon": label, "reason": reason})

    placebo_cache: dict[str, dict[int, pd.Series]] = {}
    for row in events.itertuples(index=False):
        ticker = str(row.ticker)
        px = prices.get(ticker)
        if px is None or px.empty:
            for label, _ in plan:
                skip(row, label, "no_price_data")
            continue
        event_day = pd.Timestamp(row.event_date)
        pos = px.index.searchsorted(event_day, side="left") + max(cfg.entry_lag_sessions, 0)
        if pos >= len(px.index):
            for label, _ in plan:
                skip(row, label, "event_after_price_history")
            continue
        entry_dt = px.index[pos]
        if (entry_dt - event_day).days > MAX_ENTRY_GAP_DAYS + cfg.entry_lag_sessions * 4:
            for label, _ in plan:
                skip(row, label, "no_price_at_event")
            continue
        entry_px = float(px.loc[entry_dt])
        regime = ""
        if bear is not None:
            bpos = bear.index.searchsorted(entry_dt, side="right") - 1
            if bpos >= cfg.regime_ma_sessions:
                regime = "bear" if bool(bear.iloc[bpos]) else "bull"
        cache = placebo_cache.setdefault(ticker, {})
        for label, horizon in plan:
            exit_dt = _first_on_or_after(px.index, entry_dt + pd.Timedelta(days=holding_days_for(horizon)))
            if exit_dt is None:
                skip(row, label, "not_matured")
                continue
            exit_px = float(px.loc[exit_dt])
            holding_days = int((exit_dt - entry_dt).days)
            gross = exit_px / entry_px - 1.0
            net = gross - stock_cost
            bm_net = float("nan")
            if benchmark is not None:
                b0, b1 = _first_on_or_after(benchmark.index, entry_dt), _first_on_or_after(benchmark.index, exit_dt)
                if b0 is not None and b1 is not None and b0 <= exit_dt:
                    bm_net = float(benchmark.loc[b1]) / float(benchmark.loc[b0]) - 1.0 - bench_cost
            placebo = placebo_returns(px, entry_dt, holding_days, cfg, rng, cache) - stock_cost
            pl_mean = float(placebo.mean()) if placebo.size else float("nan")
            trades.append({
                "event_type": getattr(row, "event_type", ""), "ticker": ticker, "company": getattr(row, "company", ""),
                "index_name": getattr(row, "index_name", ""), "event_date": event_day, "horizon": label, "horizon_years": horizon,
                "regime": regime, "entry_date": entry_dt, "exit_date": exit_dt, "holding_days": holding_days,
                "gross_return_pct": gross * 100.0, "return_pct": net * 100.0, "benchmark_symbol": benchmark_symbol,
                "benchmark_return_pct": bm_net * 100.0, "abnormal_return_pct": (net - bm_net) * 100.0,
                "placebo_samples": int(placebo.size), "placebo_mean_return_pct": pl_mean * 100.0,
                "excess_vs_placebo_pct": (net - pl_mean) * 100.0,
                "placebo_percentile": float((placebo < net).mean() * 100.0) if placebo.size else float("nan"),
            })
    cols = ["ticker", "event_date", "horizon", "reason"]
    return pd.DataFrame(trades), pd.DataFrame(skipped, columns=cols)


# ----------------------------------------------------------------------------- calendar time

def _price_at_or_before(series: pd.Series, ts: pd.Timestamp) -> float:
    pos = series.index.searchsorted(ts, side="right") - 1
    return float(series.iloc[pos]) if pos >= 0 else float("nan")


def calendar_time_portfolio(trades_h: pd.DataFrame, prices: Mapping[str, pd.Series], benchmark: pd.Series | None) -> pd.DataFrame:
    """Monthly frame (month_end, holdings, strategy_return, benchmark_return, excess_return): every
    month, the equal-weighted return of all positions inside their trade window of this horizon
    against the benchmark over the *same* sub-window (partial in the entry/exit month)."""
    cols = ["month_end", "holdings", "strategy_return", "benchmark_return", "excess_return"]
    if trades_h.empty or benchmark is None or benchmark.empty:
        return pd.DataFrame(columns=cols)
    t = trades_h[["ticker", "entry_date", "exit_date"]].copy()
    t["entry_date"], t["exit_date"] = pd.to_datetime(t["entry_date"]), pd.to_datetime(t["exit_date"])
    first = t["entry_date"].min().to_period("M").to_timestamp(how="end").normalize()
    last = t["exit_date"].max().to_period("M").to_timestamp(how="end").normalize()
    month_ends = pd.date_range(first, last, freq="ME")
    per_month: dict[pd.Timestamp, list[tuple[float, float]]] = {m: [] for m in month_ends}
    for row in t.itertuples(index=False):
        px = prices.get(str(row.ticker))
        if px is None or px.empty:
            continue
        active = month_ends[(month_ends >= row.entry_date) & (month_ends <= row.exit_date + pd.offsets.MonthEnd(0))]
        for m in active:
            start = max((m - pd.offsets.MonthEnd(1)).normalize(), row.entry_date)
            end = min(m, row.exit_date)
            if start >= end:
                continue
            p0, p1 = _price_at_or_before(px, start), _price_at_or_before(px, end)
            b0, b1 = _price_at_or_before(benchmark, start), _price_at_or_before(benchmark, end)
            if p0 > 0 and b0 > 0 and not np.isnan(p1) and not np.isnan(b1):
                per_month[m].append((p1 / p0 - 1.0, b1 / b0 - 1.0))
    rows = []
    for m in month_ends:
        pairs = per_month[m]
        if pairs:
            strat, bench = float(np.mean([s for s, _ in pairs])), float(np.mean([b for _, b in pairs]))
            rows.append({"month_end": m, "holdings": len(pairs), "strategy_return": strat, "benchmark_return": bench, "excess_return": strat - bench})
    return pd.DataFrame(rows, columns=cols)


def _sharpe(r: np.ndarray) -> float:
    sd = r.std(ddof=1)
    return float(r.mean() / sd * np.sqrt(12.0)) if sd > 0 else float("nan")


def _max_drawdown_pct(r: np.ndarray) -> float:
    curve = np.cumprod(1.0 + r)
    return float(((curve / np.maximum.accumulate(curve)) - 1.0).min() * 100.0)


def calendar_time_stats(ct: pd.DataFrame) -> dict[str, float]:
    """Alpha (annualized mean monthly excess), its t-statistic, Sharpe ratios (zero risk-free rate),
    volatility and max drawdown of both legs over the same months."""
    keys = ["ct_mean_monthly_excess_pct", "ct_annualized_alpha_pct", "ct_t_stat", "ct_information_ratio", "ct_strategy_sharpe",
            "ct_benchmark_sharpe", "ct_strategy_vol_pct", "ct_benchmark_vol_pct", "ct_strategy_max_dd_pct", "ct_benchmark_max_dd_pct"]
    if ct.empty or len(ct) < 2:
        return {"ct_months": int(len(ct)), **{k: float("nan") for k in keys}}
    ex, st, bm = (ct[c].to_numpy(dtype=float) for c in ("excess_return", "strategy_return", "benchmark_return"))
    return {"ct_months": int(len(ex)), "ct_mean_monthly_excess_pct": float(ex.mean() * 100.0),
            "ct_annualized_alpha_pct": float(ex.mean() * 12.0 * 100.0), "ct_t_stat": t_stat(ex), "ct_information_ratio": _sharpe(ex),
            "ct_strategy_sharpe": _sharpe(st), "ct_benchmark_sharpe": _sharpe(bm),
            "ct_strategy_vol_pct": float(st.std(ddof=1) * np.sqrt(12.0) * 100.0), "ct_benchmark_vol_pct": float(bm.std(ddof=1) * np.sqrt(12.0) * 100.0),
            "ct_strategy_max_dd_pct": _max_drawdown_pct(st), "ct_benchmark_max_dd_pct": _max_drawdown_pct(bm)}


# ----------------------------------------------------------------------------- summary

def summarize(trades: pd.DataFrame, skipped: pd.DataFrame, prices: Mapping[str, pd.Series], benchmark: pd.Series | None,
              benchmark_symbol: str, cfg: StudyConfig) -> StudyResult:
    n_h = len(cfg.horizons_years)
    adj_level = 1.0 - (1.0 - cfg.confidence_level) / n_h
    rows, by_year, by_index, by_regime, ct_all = [], [], [], [], {}
    for h in cfg.horizons_years:
        label = horizon_label(h)
        g = trades[trades["horizon"] == label].sort_values("entry_date") if not trades.empty else trades
        sk = skipped[skipped["horizon"] == label] if not skipped.empty else skipped
        rng = np.random.default_rng(cfg.seed + int(round(h * 1000)))
        r = g["return_pct"].to_numpy(dtype=float) if len(g) else np.array([])
        ab = g["abnormal_return_pct"].to_numpy(dtype=float) if len(g) else np.array([])
        ex = g["excess_vs_placebo_pct"].to_numpy(dtype=float) if len(g) else np.array([])
        row: dict[str, Any] = {"horizon": label, "horizon_years": h, "trades": int(len(g)),
                               "skipped_not_matured": int((sk["reason"] == "not_matured").sum()) if len(sk) else 0,
                               "skipped_no_price_data": int((sk["reason"] == "no_price_data").sum()) if len(sk) else 0,
                               "benchmark_symbol": benchmark_symbol}
        if len(g) == 0:
            rows.append(row)
            continue
        lo, hi = bootstrap_mean_ci(ab, rng, cfg.confidence_level, cfg.n_bootstrap)
        alo, ahi = bootstrap_mean_ci(ab, rng, adj_level, cfg.n_bootstrap)
        elo, ehi = bootstrap_mean_ci(ex, rng, cfg.confidence_level, cfg.n_bootstrap)
        ealo, eahi = bootstrap_mean_ci(ex, rng, adj_level, cfg.n_bootstrap)
        n_is = int(round(len(g) * cfg.in_sample_fraction))
        is_ab, oos_ab = ab[:n_is], ab[n_is:]
        ev_dates = pd.to_datetime(g["event_date"])
        cutoff = ev_dates.max() - pd.Timedelta(days=int(round(365.25 * cfg.recent_years)))
        rec = g[ev_dates >= cutoff]
        row.update({
            "mean_holding_days": float(g["holding_days"].mean()),
            "mean_return_pct": float(np.nanmean(r)), "median_return_pct": float(np.nanmedian(r)),
            "win_rate_pct": float((r > 0).mean() * 100.0),
            "benchmark_mean_return_pct": float(np.nanmean(g["benchmark_return_pct"])),
            "mean_abnormal_return_pct": float(np.nanmean(ab)), "median_abnormal_return_pct": float(np.nanmedian(ab)),
            "winsorized_mean_abnormal_pct": winsorized_mean(ab),
            "abnormal_ci_low_pct": lo, "abnormal_ci_high_pct": hi, "abnormal_adj_ci_low_pct": alo, "abnormal_adj_ci_high_pct": ahi,
            "abnormal_t_stat": t_stat(ab), "beat_benchmark_pct": float(np.nanmean(ab > 0) * 100.0),
            "placebo_mean_return_pct": float(np.nanmean(g["placebo_mean_return_pct"])),
            "mean_excess_vs_placebo_pct": float(np.nanmean(ex)), "median_excess_vs_placebo_pct": float(np.nanmedian(ex)),
            "winsorized_mean_excess_vs_placebo_pct": winsorized_mean(ex),
            "excess_vs_placebo_ci_low_pct": elo, "excess_vs_placebo_ci_high_pct": ehi,
            "excess_vs_placebo_adj_ci_low_pct": ealo, "excess_vs_placebo_adj_ci_high_pct": eahi,
            "excess_vs_placebo_t_stat": t_stat(ex), "mean_placebo_percentile": float(np.nanmean(g["placebo_percentile"])),
            "confidence_level": cfg.confidence_level, "adjusted_confidence_level": adj_level,
            "is_trades": int(n_is), "oos_trades": int(len(g) - n_is),
            "is_mean_abnormal_pct": float(np.nanmean(is_ab)) if n_is else float("nan"),
            "oos_mean_abnormal_pct": float(np.nanmean(oos_ab)) if len(oos_ab) else float("nan"),
            "oos_mean_excess_vs_placebo_pct": float(np.nanmean(ex[n_is:])) if len(oos_ab) else float("nan"),
            "recent_years": cfg.recent_years, "recent_window_start": str(cutoff.date()), "recent_trades": int(len(rec)),
            "recent_mean_abnormal_pct": float(rec["abnormal_return_pct"].mean()) if len(rec) else float("nan"),
            "recent_mean_excess_vs_placebo_pct": float(rec["excess_vs_placebo_pct"].mean()) if len(rec) else float("nan"),
        })
        for regime in ("bear", "bull"):
            gr = g[g["regime"] == regime]
            row[f"{regime}_trades"] = int(len(gr))
            row[f"{regime}_mean_abnormal_pct"] = float(gr["abnormal_return_pct"].mean()) if len(gr) else float("nan")
            row[f"{regime}_mean_excess_vs_placebo_pct"] = float(gr["excess_vs_placebo_pct"].mean()) if len(gr) else float("nan")
            row[f"{regime}_beat_benchmark_pct"] = float((gr["abnormal_return_pct"] > 0).mean() * 100.0) if len(gr) else float("nan")
            by_regime.append({"horizon": label, "regime": regime, "trades": int(len(gr)),
                              "mean_abnormal_pct": row[f"{regime}_mean_abnormal_pct"],
                              "mean_excess_vs_placebo_pct": row[f"{regime}_mean_excess_vs_placebo_pct"]})
        ct = calendar_time_portfolio(g, prices, benchmark) if benchmark is not None else pd.DataFrame()
        ct_all[label] = ct
        row.update(calendar_time_stats(ct))
        rows.append(row)
        for year, gy in g.groupby(pd.to_datetime(g["event_date"]).dt.year):
            by_year.append({"horizon": label, "year": int(year), "trades": int(len(gy)),
                            "mean_return_pct": float(gy["return_pct"].mean()), "mean_abnormal_pct": float(gy["abnormal_return_pct"].mean()),
                            "beat_benchmark_pct": float((gy["abnormal_return_pct"] > 0).mean() * 100.0),
                            "mean_excess_vs_placebo_pct": float(gy["excess_vs_placebo_pct"].mean())})
        for idx, gi in g.groupby("index_name"):
            by_index.append({"horizon": label, "index_name": idx, "trades": int(len(gi)),
                             "mean_return_pct": float(gi["return_pct"].mean()), "mean_abnormal_pct": float(gi["abnormal_return_pct"].mean()),
                             "beat_benchmark_pct": float((gi["abnormal_return_pct"] > 0).mean() * 100.0),
                             "mean_excess_vs_placebo_pct": float(gi["excess_vs_placebo_pct"].mean())})
    return StudyResult(trades=trades, skipped=skipped, summary=pd.DataFrame(rows), breakdown_by_year=pd.DataFrame(by_year),
                       breakdown_by_index=pd.DataFrame(by_index), breakdown_by_regime=pd.DataFrame(by_regime),
                       calendar_time=ct_all, benchmark_symbol=benchmark_symbol)


def run_event_study(events: pd.DataFrame, prices: Mapping[str, pd.Series], benchmark: pd.Series | None, benchmark_symbol: str = "",
                    cfg: StudyConfig | None = None) -> StudyResult:
    """Events (from load_events) + prices (dict ticker -> adjusted closes) + spliced benchmark -> StudyResult."""
    cfg = cfg or StudyConfig()
    if "event_date" not in events.columns:
        events = events.assign(event_date=events["filing_date"])
    trades, skipped = build_trades(events, prices, benchmark, benchmark_symbol, cfg)
    return summarize(trades, skipped, prices, benchmark, benchmark_symbol, cfg)


# ----------------------------------------------------------------------------- comparison

COMPARE_COLUMNS = ("trades", "mean_return_pct", "median_return_pct", "benchmark_mean_return_pct", "mean_abnormal_return_pct",
                   "beat_benchmark_pct", "placebo_mean_return_pct", "mean_excess_vs_placebo_pct", "abnormal_adj_ci_low_pct",
                   "abnormal_adj_ci_high_pct", "ct_annualized_alpha_pct", "ct_t_stat")


def compare_with_shipped(yours: pd.DataFrame, shipped: pd.DataFrame, columns=COMPARE_COLUMNS) -> pd.DataFrame:
    """Side-by-side table of your summary vs the shipped one, per horizon and column, with the difference."""
    rows = []
    for _, s in shipped.iterrows():
        y = yours[yours["horizon"] == s["horizon"]]
        for c in columns:
            if c not in s or c not in yours.columns:
                continue
            mine = float(y[c].iloc[0]) if len(y) else float("nan")
            rows.append({"horizon": s["horizon"], "metric": c, "shipped": float(s[c]), "yours": mine, "diff": mine - float(s[c])})
    return pd.DataFrame(rows)
