# Provenance and rights of every column

| Data | Source | Terms | How it enters the dataset |
|---|---|---|---|
| Filings, items, form type, filer name, CIK, accession number, filing date, period of report, SIC, state of incorporation | SEC EDGAR full-text search (`efts.sec.gov/LATEST/search-index`) and filing indexes on sec.gov | US federal government work, public domain; SEC fair-access policy (identify yourself, ≤ 10 requests/s) | fetched per item and year, stored as raw hits, normalised by the event rule |
| Acceptance timestamp | the filing's index page on sec.gov (`<accession>-index.htm`; older filings: the header of `<accession>.txt`) | as above | fetched per filing, cached (`tools/sec_acceptance.py` in the build) |
| Ticker | EDGAR's display name for the CIK **at fetch time** (2026-09) | as above | `ticker_mapping = edgar_current`. EDGAR shows the symbol the company trades under today; a company that changed its symbol, was acquired or delisted may carry today's symbol, no symbol, or a successor's. Historical symbol changes are **not** reconstructed in v1 |
| S&P 500 membership, point in time | `fja05680/sp500` on GitHub (`sp500_ticker_start_end.csv`), itself compiled from public index-change announcements and Wikipedia | the repository states no explicit licence; the underlying facts (which company joined or left an index on which date) are public announcements. Index names, their composition history and the sources for it can carry trademark or database rights: this is an open question in the seller's legal brief, not a settled one | used only as a **filter** (`point_in_time = True` rows are members at the filing date); the membership table itself is not redistributed. Index names are used descriptively, not as a licensed index product |
| NASDAQ-100 membership | current list at fetch time (Wikipedia) | CC BY-SA text; used as a fact filter only | `point_in_time = False`; Item 2.05 only; 20 events |
| Trading calendar | days with a Yahoo Finance close for SPY | derived fact (which days the US market traded) | `first_full_session`, `benchmark_entry_date` |
| Aggregate statistics (`data/benchmarks/`) | computed by the seller from Yahoo Finance adjusted closes with the shipped methodology | Yahoo's terms forbid redistribution of *their data*. The dataset therefore contains no prices and no per-trade rows, and the prices cannot be reconstructed from it. Whether commercially published *derived aggregates* fall outside those terms is documented here rather than asserted: it is an open question in the seller's legal brief. The tables are provided as the seller's own derived statistics and as methodological example output | means, medians, CIs, breakdowns, monthly portfolio returns |
| Code | written by the seller | MIT licence for the code portion (see `licenses/`) | `code/` |

What you must bring: prices. The engine takes any `dict[ticker, pd.Series]` of adjusted closes. The
`load_prices_yfinance` helper exists for personal research under Yahoo's own terms; for commercial use of
prices, use a vendor whose licence covers your use.

Nothing in the dataset identifies a natural person. Filers are companies; officers named in filings are not
extracted.
