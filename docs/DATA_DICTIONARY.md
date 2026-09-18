# Data dictionary

All files are UTF-8 CSV with a header row, decimal point, dates as `YYYY-MM-DD`, percentages as plain
numbers (`7.6` = 7.6 %). Times are US Eastern as stated by EDGAR (no time zone suffix).

## `data/events/<event_class>.csv` — one row per event

| Column | Type | Meaning | Source |
|---|---|---|---|
| `event_id` | string | `<item>-<accession_no>`, stable across dataset versions | derived |
| `event_class` | string | `item_2_05_restructuring`, `item_2_06_impairment`, `item_4_02_restatement` | rule |
| `item` | string | the 8-K item that defines the class (`2.05`, `2.06`, `4.02`) | EDGAR |
| `form_type` | string | `8-K` or `8-K/A` (amendment) | EDGAR full-text search |
| `ticker` | string | trading symbol EDGAR lists for the filer's CIK **at fetch time** (see `ticker_mapping`) | EDGAR |
| `company` | string | filer name as listed by EDGAR | EDGAR |
| `cik` | integer | SEC Central Index Key of the filer | EDGAR |
| `accession_no` | string | EDGAR accession number `0000000000-00-000000` | EDGAR |
| `filing_date` | date | date EDGAR recorded the filing | EDGAR |
| `accepted_at_et` | datetime | EDGAR acceptance timestamp (US Eastern), empty if not retrievable | EDGAR filing index |
| `event_session` | string | `pre_market` (accepted before 09:30), `market_hours` (09:30 to 16:00), `after_market`, `non_trading_day`, `unknown` | derived |
| `first_full_session` | date | first US trading session that opens after acceptance: same day for `pre_market`, next session otherwise | derived (calendar = days with an SPY close) |
| `benchmark_entry_date` | date | the entry session our aggregates used: first session on/after `filing_date` **plus one** (`entry_lag_sessions: 1` in `run.json`) | derived |
| `period_of_report` | date | "period of report" field of the filing (usually the event date named in the 8-K) | EDGAR |
| `index_name` | string | `SP500` or `NASDAQ100` | universe table |
| `point_in_time` | bool | `True`: membership verified at `filing_date`; `False`: current members list (NASDAQ-100 only) | universe table |
| `in_benchmark_run` | bool | `True`: this event is one the shipped aggregates in `data/benchmarks/<class>/` were computed from. Item 2.05 carries 20 extra NASDAQ-100 events with `False`; pass `benchmark_subset=True` to `load_events` to reproduce our tables exactly | rule |
| `items_in_filing` | string | every 8-K item in that filing, comma separated (a filing can carry 2.05 and 2.06) | EDGAR |
| `sic_code` | string | Standard Industrial Classification code of the filer | EDGAR |
| `state_of_inc` | string | state of incorporation | EDGAR |
| `source_url` | string | the filing's folder on sec.gov (documents and index) | EDGAR |
| `confidence` | float | `1.0` for all v1 rows: the class is defined by the item itself, no text classification | rule |
| `ticker_mapping` | string | `edgar_current`: see PROVENANCE.md; historical symbol changes are not tracked | rule |
| `rule_version` | string | `item_filter_v1` | rule |

**Event rule (v1):** every Form 8-K (or 8-K/A) that carries the item, filed 2005-01-01 to 2025-12-31 by a
filer with a ticker in EDGAR; filings by the same ticker within 365 days of an earlier kept filing are
collapsed into the earlier one (follow-ups to the same plan); the filer must be a member of the index at the
filing date. Exclusions are listed, not dropped.

## `data/excluded_events.csv` — every raw hit that did not become an event

Columns as above plus `reason`: `no_ticker_in_edgar` (the CIK has no trading symbol in EDGAR, mostly
delisted or private filers; this is the survivorship hole, see KNOWN_LIMITATIONS.md),
`follow_up_within_365d`, `not_index_member_at_filing`, `outside_date_range`, and a handful of `not_in_canonical_run` (passed our re-derivation of the rule but were not in the original run, mostly filers with several tickers where the run picked another symbol; kept visible rather than silently added).

## `data/benchmarks/<event_class>/`

| File | Content |
|---|---|
| `run.json` | exact parameters of our run: horizons, entry lag, costs, benchmark candidates, event rule, universe, evaluation settings, timestamp |
| `summary.csv` | one row per holding horizon (`0.1y`, `1y`, `3y`, `5y` where run); columns below |
| `breakdown_by_year.csv` | per horizon and filing year: trades, mean return, mean abnormal, share beating the benchmark, mean excess vs placebo |
| `breakdown_by_index.csv` | same per index |
| `breakdown_by_regime.csv` | same for `bear` / `bull` entries (benchmark below / above its 200-session average at entry) |
| `calendar_time_<h>.csv` | monthly series of the calendar-time portfolio: `month_end, holdings, strategy_return, benchmark_return, excess_return` (fractions, not %) |
| `verdict.json` | our verdict per horizon with every criterion, pass/fail and the numbers behind it |
| `coverage.csv` | events that could not be evaluated per horizon and why (`no_price_data`, `not_matured`, `no_price_at_event`) |

### `summary.csv` columns (main ones; the engine emits the same names)

| Column | Meaning |
|---|---|
| `trades` | matured event × horizon pairs with prices |
| `mean_return_pct`, `median_return_pct`, `win_rate_pct` | buy-and-hold return net of costs; share of trades > 0 |
| `benchmark_mean_return_pct` | spliced MSCI World proxy (`benchmark_symbol`) over exactly the same dates, net of costs |
| `mean_abnormal_return_pct`, `median_abnormal_return_pct`, `winsorized_mean_abnormal_pct` | return minus benchmark (BHAR); 5 % winsorized mean |
| `abnormal_ci_low_pct`, `abnormal_ci_high_pct` | bootstrap CI of the mean abnormal return (2000 resamples) at `confidence_level` |
| `abnormal_adj_ci_low_pct`, `abnormal_adj_ci_high_pct` | same at the Bonferroni-adjusted level for the number of horizons (`adjusted_confidence_level`) |
| `abnormal_t_stat`, `beat_benchmark_pct` | t-statistic of the mean; share of trades with abnormal > 0 |
| `placebo_mean_return_pct`, `mean_excess_vs_placebo_pct`, `excess_vs_placebo_*ci*`, `mean_placebo_percentile` | same stock, same holding length, 200 random other entries within ±10 years and ≥ 30 days away |
| `is_*`, `oos_*` | first 60 % of trades by entry date vs the rest |
| `recent_*` | trades whose filing lies in the last 5 years before the latest matured filing |
| `bear_*`, `bull_*` | regime at entry |
| `stress_*`, `hidden_event_ratio` | survivorship stress: known missing and estimated hidden events added as full-loss trades |
| `ct_*` | calendar-time portfolio: months, annualized alpha, t-stat, information ratio, Sharpe of both legs, volatility, max drawdown, annual return |
| `portfolio_*` | a capital-constrained simulation (initial capital 10,000, stake 1,000 per trade) |

## `sample/`

`events_sample.csv` (30 events per class, spread over the years), `excluded_events_sample.csv`,
`summary_<class>.csv` (rounded headline columns). Evaluation use only.
