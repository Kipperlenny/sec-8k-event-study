"""Offline tests on synthetic prices: the engine's definitions, not any real result."""
import numpy as np
import pandas as pd
import pytest

from sec_events.loader import validate_events
from sec_events.prices import spliced_benchmark
from sec_events.study import StudyConfig, build_trades, holding_days_for, run_event_study


def _series(start: str, n: int, daily: float, seed: int = 0) -> pd.Series:
    idx = pd.bdate_range(start, periods=n)
    rng = np.random.default_rng(seed)
    return pd.Series(100.0 * np.cumprod(1.0 + daily + rng.normal(0, 0.0, n)), index=idx, name="close")


def _events(rows):
    df = pd.DataFrame(rows, columns=["ticker", "filing_date"])
    df["event_class"], df["item"], df["company"], df["cik"] = "test_class", "2.05", "Test Co", 1
    df["event_id"], df["form_type"] = "2.05-0000000001-05-000001", "8-K"
    df["accession_no"] = "0000000001-05-000001"
    df["index_name"], df["point_in_time"], df["items_in_filing"] = "SP500", True, "2.05"
    df["source_url"], df["confidence"] = "https://www.sec.gov/", 1.0
    return df


def test_entry_exit_and_costs():
    px = _series("2010-01-01", 800, 0.001)          # smooth +0.1 %/session
    bm = _series("2010-01-01", 800, 0.0005)
    ev = validate_events(_events([("AAA", "2010-03-05")]))  # a Friday
    ev["event_date"] = ev["filing_date"]
    cfg = StudyConfig(horizons_years=(1.0,), placebo_samples=10)
    trades, skipped = build_trades(ev, {"AAA": px}, bm, "BM", cfg)
    assert len(trades) == 1 and skipped.empty
    t = trades.iloc[0]
    assert t["entry_date"] == pd.Timestamp("2010-03-08")  # lag 1 session -> Monday
    assert (t["exit_date"] - t["entry_date"]).days >= holding_days_for(1.0)
    gross = px.loc[t["exit_date"]] / px.loc[t["entry_date"]] - 1.0
    assert t["gross_return_pct"] == pytest.approx(gross * 100.0)
    assert t["return_pct"] == pytest.approx(gross * 100.0 - 0.20)           # 20 bps
    assert t["abnormal_return_pct"] == pytest.approx(t["return_pct"] - t["benchmark_return_pct"])


def test_skips_are_explained():
    px = _series("2010-01-01", 100, 0.001)
    ev = validate_events(_events([("AAA", "2010-03-05"), ("ZZZ", "2010-03-05"), ("AAA", "2011-01-03")]))
    ev["event_date"] = ev["filing_date"]
    trades, skipped = build_trades(ev, {"AAA": px}, None, "", StudyConfig(horizons_years=(1.0,)))
    reasons = set(skipped["reason"])
    assert "no_price_data" in reasons and "not_matured" in reasons
    assert len(trades) == 0


def test_benchmark_as_its_own_event_has_zero_abnormal_return():
    bm = _series("2005-01-01", 2000, 0.0004, seed=3)
    ev = validate_events(_events([("BM", "2006-06-01"), ("BM", "2008-09-15")]))
    cfg = StudyConfig(horizons_years=(1.0,), entry_lag_sessions=0, stock_cost_bps=5.0, benchmark_cost_bps=5.0, placebo_samples=5)
    res = run_event_study(ev, {"BM": bm}, bm, "BM", cfg)
    assert res.summary.loc[0, "mean_abnormal_return_pct"] == pytest.approx(0.0, abs=1e-9)


def test_spliced_benchmark_prefers_first_candidate():
    a = pd.Series([1.0, 1.1, 1.21], index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]))
    b = pd.Series([1.0, 1.5, 2.0, 2.0], index=pd.to_datetime(["2019-12-31", "2020-01-01", "2020-01-02", "2020-01-03"]))
    sym, idx = spliced_benchmark({"A": a, "B": b}, ["A", "B"])
    assert sym == "A+B"
    assert idx.iloc[-1] / idx.iloc[-2] == pytest.approx(1.1)   # A's return where both exist
    assert idx.iloc[1] / idx.iloc[0] == pytest.approx(1.5)     # B's return before A starts


def test_validate_rejects_bad_accession():
    df = _events([("AAA", "2010-03-05")])
    df["accession_no"] = "nope"
    with pytest.raises(ValueError):
        validate_events(df)
