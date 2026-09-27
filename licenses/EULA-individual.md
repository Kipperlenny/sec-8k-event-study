# End User Licence Agreement, Individual / Academic licence

**Version 1.0, 18 September 2026.** The current text of this agreement is always the one delivered with the version of the dataset you bought.

**Dataset:** SEC 8-K Event Dataset + Reproducible Python Event Study, version 1
**Tier:** Individual / Academic licence. One-off licence fee USD 79, plus any VAT or sales tax the merchant of record charges at checkout.

## 1. Parties

**Licensor:** Lennart Schreiber, sole trader (autónomo) registered in Spain, trading under the brand "aiamond", Calle de los Sargos 4, 30383 Los Nietos, Spain, VAT ID ESY4561889Z, kontakt@webzap.eu.

**Licensee:** the one named natural person who purchased this tier through the merchant of record ("you").

Gumroad, Inc. acts as merchant of record and sells the download to you. This Agreement is between you and the Licensor and governs what you may do with the Licensed Material.

## 2. Definitions

- **Licensed Material**: the event tables in `data/events/`, the exclusions file `data/excluded_events.csv`, the aggregate tables, monthly series and verdict files in `data/benchmarks/`, and the Documentation, including their selection, labels, classifications, structure and computed statistics.
- **Code**: the loader, schema validator, event-study engine, price-provider interface, tests and sample notebook in `code/`.
- **Documentation**: the README, data dictionary, methodology, provenance, known-limitations, risk-notice and changelog files.
- **Derived Results**: anything you produce using the Licensed Material that is not the event tables themselves or a substantial part of them, for example statistics, charts, models, backtests, papers, talks or filtered subsets combined with your own data. A file that reproduces all or a substantial part of the event rows is a copy of the Licensed Material, not a Derived Result.

## 3. The Code is MIT licensed and is not restricted here

The Code is published under the MIT Licence, including publicly on GitHub, and the MIT text is in `code/LICENSE`. Nothing in this Agreement restricts, conditions or narrows your rights in the Code. You may use, modify, keep and redistribute the Code under the MIT terms, for any purpose, commercial or not.

This Agreement licenses the **data and the Documentation** only: the event tables, the exclusions file, the aggregate tables, the monthly series, the verdict files and the written documentation.

## 4. What you may do

Subject to this Agreement and payment of the fee, the Licensor grants you a non-exclusive, non-transferable, worldwide, perpetual licence, for use by **one named natural person**, to:

a) use the Licensed Material for private analysis, for academic research and teaching, and for your own commercial analysis;
b) publish aggregates, charts, conclusions and short examples drawn from the Licensed Material, with the attribution in section 6;
c) share Derived Results with co-authors and collaborators. **Co-authors do not need their own licence** as long as they do not receive the full data;
d) submit a reproduction package to a journal, repository or conference, provided the package does not contain the full dataset;
e) make backup copies for your own use.

## 5. What you may not do

You may not:

a) pass on the raw data, that is the event tables, the exclusions file or a substantial part of either, to anyone in any form, including as a download, in a public code repository, on a shared drive or through a queryable service;
b) give a laboratory, research group, department, team or employer shared access to the data. The licence is for one person;
c) make a substantial part of the event rows publicly available;
d) remove or alter copyright, licence or attribution notices;
e) use the Licensed Material to train, fine-tune or prompt a model whose purpose is to reproduce the dataset, or a substitute for it, for distribution or sale;
f) present the Licensed Material or the benchmark results as your own work without the attribution in section 6.

Facts are not owned by anyone. Nothing here stops you from collecting Form 8-K filings yourself from SEC EDGAR and building your own table. These restrictions apply to the Licensor's compiled, labelled and structured tables and statistics, not to the underlying public filings.

## 6. Attribution

Publications, talks, code and other Derived Results that show or rely on the Licensed Material carry:

> Event data: SEC 8-K Event Dataset v1 (aiamond, Lennart Schreiber), derived from SEC EDGAR Form 8-K filings. https://aiamond.com

Where space is limited, for example in a chart footnote, "Source: aiamond SEC 8-K Event Dataset v1" is acceptable.

## 7. Ownership

The Licensor owns the database and the Documentation, including the selection, cleaning, labelling, deduplication and structuring of the tables and the statistics computed from them, and retains all rights not expressly granted here. The Code is owned by the Licensor and licensed to everyone under the MIT Licence as stated in section 3.

## 8. Third-party data notice

The events derive from public Form 8-K filings retrieved through SEC EDGAR. Those filings are works of the United States government and are in the public domain.

Index membership flags come from filtering the events against public index-change information. **No membership table is redistributed**; index names are used descriptively and not as a licensed index product.

The aggregate statistics were computed by the Licensor from historical adjusted closing prices of a third-party source whose terms do not permit redistribution of that source's data. **Therefore the Licensed Material contains no prices and no per-trade rows**, and the price series cannot be reconstructed from it. The aggregates are provided as the Licensor's own derived statistics and as methodological example output. The provenance of every column is documented in `docs/PROVENANCE.md`. The Licensor grants no right in any third-party price data and cannot do so.

**You are responsible for your own price source and for complying with its licence terms** when you recompute, extend or publish anything based on prices.

## 9. No investment advice

The Licensed Material is historical research material. It is not investment advice, not a recommendation to buy or sell any security, not a trading signal, and not an offer or solicitation. The results describe what happened in the past under stated assumptions and imply no promise about future returns. The Licensor is not a registered investment adviser in any jurisdiction. Any trading or investment decision you make is yours alone.

## 10. Warranties and liability

To the maximum extent permitted by law, the Licensed Material is provided "as is" and without warranties of accuracy, completeness, fitness for a particular purpose, non-infringement, investment performance or uninterrupted availability. In particular the event tables can contain classification errors, missed filings and ticker-mapping errors, and the statistics depend on the price source used and on the limitations described in the Documentation.

The Licensor is not liable for indirect, incidental, consequential, special or lost-profit damages. The Licensor's aggregate liability arising from the Licensed Material is limited to the amount paid for this licence.

These limitations do not apply where liability cannot lawfully be excluded or limited, including liability for intent, fraud, wilful misconduct, gross negligence, death or personal injury, and mandatory consumer protection rights.

## 11. Payment, delivery, refunds and withdrawal

Gumroad, as merchant of record, administers payment, delivery, refunds and any statutory withdrawal process under the terms presented at checkout. Nothing in this EULA limits any mandatory consumer rights. If this EULA conflicts with Gumroad's checkout terms regarding payment, refunds or withdrawal, those checkout terms control; this EULA continues to govern the licence and permitted use of the data.

## 12. No support, no updates

The fee covers this version only. There is no entitlement to support, to a service level, or to updates, corrections, new event classes or new versions; these may be offered separately. The Licensor may answer questions about documented standard cases at its discretion.

## 13. Term and termination

This licence runs indefinitely from purchase. The Licensor may terminate the licence for a material breach that is not cured within 14 days after notice, except that deliberate unauthorised redistribution may result in immediate termination.

On termination you delete all copies of the Licensed Material. The redistribution bans in section 5 survive termination, as do sections 6 to 10 and 14. Derived Results published before termination in compliance with this Agreement may remain published.

## 14. Governing law and jurisdiction

This Agreement is governed by the laws of Spain, without depriving consumers of mandatory protections available under the law of their habitual residence. For business users, the courts at the Licensor's registered place of business in Spain have exclusive jurisdiction. Consumers may bring claims in any court available to them under mandatory law.

## 15. Severability and entire agreement

If any provision is invalid or unenforceable, the rest remains in force and the provision is replaced by a valid one that comes closest to its purpose.

This Agreement, the MIT Licence for the Code, and the merchant of record's checkout terms are the entire agreement about the Licensed Material and replace earlier statements. Changes require written form. Listing text and Documentation describe the product; they do not add rights beyond this Agreement.

## 16. Version

EULA Individual / Academic, v1, 2026-09-18. The version you accepted at purchase applies to your copy; later versions apply only to later purchases.
