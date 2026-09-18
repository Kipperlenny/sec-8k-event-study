# SEC 8-K event study: open tooling, sample data

Python tooling to run reproducible event studies on SEC Form 8-K filings, and a sample of the
[SEC 8-K Event Dataset](https://aiamond.gumroad.com/l/sec-8k-events?utm_source=github&utm_medium=readme&utm_campaign=sec8k) it was built for.

The code here is **MIT licensed and complete**: the loader with schema validation, the event-study engine
(entry rules, costs, benchmark over the same dates, abnormal returns, bootstrap confidence intervals,
placebo, calendar-time portfolio, breakdowns), the price-provider interface, the tests and the notebook.
Point it at your own events and your own prices and it works.

What is **not** here is the assembled data: 983 labelled events across three 8-K item classes with
SEC acceptance timestamps, trading sessions, point-in-time index membership and the full exclusions file
(21,654 filings with the reason each was dropped), plus our computed benchmark tables. That is the
paid part, because assembling and checking it is the part an afternoon of code generation does not give
you. A 90-event sample with every production column is in [`sample/`](sample/).

## Quick start

```bash
pip install -e code
python -m pytest code/tests
```

```python
from sec_events import load_events, load_prices_yfinance, spliced_benchmark, run_event_study

ev = load_events("sample/events_sample.csv")          # or your own table with the same columns
prices = load_prices_yfinance(sorted(set(ev.ticker)) + ["URTH", "ACWI", "SPY"])
symbol, benchmark = spliced_benchmark(prices)
res = run_event_study(ev, prices, benchmark, symbol)
print(res.summary[["horizon", "trades", "mean_return_pct", "mean_abnormal_return_pct"]])
```

Prices are never included, here or in the paid dataset: bring a source whose terms allow your use
([PROVENANCE.md](docs/PROVENANCE.md)).

## What the engine computes

Entry one session after the filing, exit after a fixed horizon, costs deducted, benchmark over exactly the
same dates, abnormal return, a seeded placebo of random other entry days in the same stock, bootstrap
confidence intervals with a Bonferroni adjustment across horizons, in-sample and out-of-sample split,
most-recent-years check, bull and bear regimes, and a calendar-time portfolio so clustered events are not
counted as independent observations. The rules are in [METHODOLOGY.md](docs/METHODOLOGY.md); the honest
limits, including two open data-rights questions, are in [KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md).

## The full dataset

983 events, 2005 to 2025, S&P 500 point-in-time members (Item 2.05 also carries current NASDAQ-100
members, flagged): Item 2.05 restructuring, Item 2.06 impairment, Item 4.02 restatement. With our benchmark
tables, verdict files and the complete exclusions file. One-off licences, Individual 79 USD, Organization
249 USD, Product/Publication 599 USD: **[https://aiamond.gumroad.com/l/sec-8k-events](https://aiamond.gumroad.com/l/sec-8k-events?utm_source=github&utm_medium=readme&utm_campaign=sec8k)**

Results are reported as the data supports them, including negative ones: buying after a restatement
(Item 4.02) underperformed the benchmark over three years, and that table ships with the rest.

Not investment advice. See [RISK_NOTICE.md](RISK_NOTICE.md).
