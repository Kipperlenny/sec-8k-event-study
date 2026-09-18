# Methodology

The question an event rule like "buy when a company files X, sell N years later" raises has two parts:
**selection** (do the companies the rule picks go up?) and **timing** (is buying *at the filing* better than
buying the same stock at another time?). A comparison with the index answers only the first; the placebo
answers the second. Every number in `data/benchmarks/` and every number the engine produces follows the
definitions below.

## Events

Events come from a regulatory source that lists *every* occurrence, not from memory or news: EDGAR full-text
search for Form 8-K filings carrying the item (2.05: costs associated with exit or disposal activities;
2.06: material impairments; 4.02: non-reliance on previously issued financial statements). Filings by the
same ticker within 365 days of an earlier kept filing are collapsed into it (updates to the same plan).
The filer must be a member of the index at the filing date (S&P 500 point in time; NASDAQ-100 current list,
flagged). Everything excluded is listed in `data/excluded_events.csv` with the reason.

## Per event and horizon

| Quantity | Definition |
|---|---|
| Entry | first session on or after the filing date, plus `entry_lag_sessions` (1: filings often land after the close) |
| Exit | first session on or after entry + round(365.25 × horizon years) days |
| Return | exit close / entry close − 1, minus `stock_round_trip_bps` (20), on adjusted closes |
| Benchmark return | spliced MSCI World proxy (URTH; ACWI before 2012; SPY before 2008) over the same dates, minus `benchmark_round_trip_bps` (5) |
| Abnormal return | return − benchmark return (buy-and-hold abnormal return, BHAR) |
| Placebo | same stock, same holding length, 200 random entry days within ±10 years of the entry and ≥ 30 days away; seeded |
| Excess vs placebo | return − mean placebo return; placebo percentile = share of placebo returns below the actual |

Trades that cannot be evaluated are listed with a reason (`no_price_data`: no price history for the ticker;
`no_price_at_event`: history starts more than ten days after the filing; `not_matured`: exit beyond the data).

## Per horizon

Mean, median, win rate, share beating the benchmark, t-statistic, bootstrap CI of the mean (2000 resamples,
seeded) at the configured level and at a Bonferroni-adjusted level for the number of horizons, 5 %
winsorized means. Robustness:

- **In-sample / out-of-sample:** trades ordered by entry; first 60 % vs the rest. The rule has no fitted
  parameters, so this is a stability check.
- **Most recent years:** trades filed in the last 5 years before the latest matured filing of the horizon.
- **Regime:** bear = benchmark below its 200-session moving average at entry.
- **Calendar-time portfolio** (Fama 1998; Mitchell and Stafford 2000): every month, the equal-weighted return
  of all positions inside their event window against the benchmark over the same sub-window (partial months
  in the entry and exit month). One observation per month, whatever the number of active events, which is
  the standard correction for clustered events. Reported as annualized alpha (12 × mean monthly excess),
  its t-statistic, information ratio, Sharpe ratios of both legs (zero risk-free rate), volatility, max drawdown.
- **Survivorship stress** (shipped tables only, `stress_*` columns): events of members whose price history is
  gone, plus an estimate of events never seen because the filer is delisted and has no ticker in EDGAR,
  are added as full-loss trades and the statistics recomputed. Deliberately punitive.

## Verdict (shipped `verdict.json`)

Per horizon, twelve criteria with pass/fail and numbers: sample size ≥ 30; beats the benchmark (adjusted CI
above zero); beats the placebo (adjusted CI above zero); ≥ 2 % annualized abnormal return; positive out of
sample; positive in the recent years; calendar-time t ≥ 2; Sharpe ≥ benchmark's; positive vs placebo in both
regimes; winsorized means positive; survives the survivorship stress; more than half of the trades beat the
benchmark. GREAT IDEA needs all; WEAK EDGE beats the benchmark but fails at least one; NO EDGE rules an
edge out; YOU LOST has the adjusted CI entirely below zero; INCONCLUSIVE otherwise. The verdict reports
what the data supports, including null and negative results.

## References

Barber and Lyon (1997), *Detecting long-run abnormal stock returns*, JFE. Fama (1998), *Market efficiency,
long-term returns, and behavioral finance*, JFE. Mitchell and Stafford (2000), *Managerial decisions and
long-term stock price performance*, J. Business. Kothari and Warner, *Econometrics of event studies*,
Handbook of Corporate Finance. SEC Form 8-K instructions: https://www.sec.gov/files/form8-k.pdf
