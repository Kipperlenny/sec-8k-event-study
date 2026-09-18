# Known limitations (read before you trust a number)

1. **Survivorship, two holes.** (a) Yahoo Finance serves no history for delisted tickers, so events of
   companies that were later acquired or went bankrupt are in the event table but not in the aggregates
   (`coverage.csv`: `no_price_data`, 6 to 11 % of events per class). (b) EDGAR shows no ticker for delisted
   filers, so their filings never became events at all (`excluded_events.csv`: `no_ticker_in_edgar`). The
   shipped `stress_*` statistics count both as full losses; the S&P 500 point-in-time filter estimates the
   hidden share at about 20 % of seen events. Your own price source may close hole (a) partially; hole (b)
   needs a historical CIK-to-ticker mapping, which v1 does not ship.
2. **Ticker mapping is "as EDGAR lists it today"** (`ticker_mapping = edgar_current`). Symbol changes,
   reverse mergers and successor entities are not reconstructed. Check `company` and `cik` when a ticker
   looks wrong; the CIK is stable.
3. **Point-in-time membership only for the S&P 500.** NASDAQ-100 rows (`point_in_time = False`, Item 2.05
   only, 20 events) use the current members list and therefore flatter results.
4. **Blunt event definition.** Item 2.05 covers a small plant closure as well as a company-wide restructuring;
   Item 2.06 a minor write-down as well as a goodwill impairment of half the balance sheet. No size filter
   in v1; the filing text is one link away (`source_url`).
5. **Timing.** Our aggregates enter one session after the first session on or after the filing date
   (`benchmark_entry_date`), a conservative rule that ignores the acceptance time. `accepted_at_et`,
   `event_session` and `first_full_session` are provided so you can enter at the first full session instead.
   Acceptance timestamps are missing for a small number of filings (`event_session = unknown`).
6. **Overlapping windows** inflate per-trade confidence intervals; trust the calendar-time t-statistic more
   when they disagree.
7. **Adjusted closes drift.** Vendors re-adjust for every dividend, so a re-run on fresh data moves means by
   a few tenths of a point and can add or drop a trade near a data boundary. Measured on 2026-09-18: Item
   2.06, 1-year mean abnormal 6.50 → 6.45 pp, 297 → 297 trades, 3-year 276 → 275 trades, on Yahoo data two
   weeks apart. Item 4.02 (run and dataset built the same day) reproduces to the last digit.
8. **Costs and FX.** Flat 20 bps round trip on stocks, 5 bps on the benchmark; no FX, no intraday execution,
   no borrowing, no taxes.
9. **Time range.** Filings 2005-01-01 to 2025-12-31; 8-K Items 2.05/2.06 exist since August 2004, 4.02 since
   the same reform. Later horizons of 2023 to 2025 events are not matured (`not_matured`).
10. **Two rights questions are documented, not settled.** (a) The index membership flag is the result of
    filtering against public index-change information; no membership table is redistributed, and index
    names are used descriptively. (b) Our aggregates were computed from a price source whose terms forbid
    redistribution, which is why no prices and no per-trade rows are shipped and none can be reconstructed;
    whether commercially published derived aggregates fall outside those terms is an open question we state
    rather than assert. See `docs/PROVENANCE.md`.
11. **Nothing here predicts anything.** The tables describe what happened after past filings under one
    specific rule. See `RISK_NOTICE.md`.
