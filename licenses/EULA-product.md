# End User Licence Agreement, Product / Publication licence

**Version 1.0, 18 September 2026.** The current text of this agreement is always the one delivered with the version of the dataset you bought.

**Dataset:** SEC 8-K Event Dataset + Reproducible Python Event Study, version 1
**Tier:** Product / Publication licence, one legal entity and one named external product or publication. One-off licence fee USD 599, plus any VAT or sales tax the merchant of record charges at checkout.

## 1. Parties

**Licensor:** Lennart Schreiber, sole trader (autónomo) registered in Spain, trading under the brand "aiamond", Calle de los Sargos 4, 30383 Los Nietos, Spain, VAT ID ESY4561889Z, kontakt@webzap.eu.

**Licensee:** the single legal entity (company, partnership, sole trader or other organisation) on whose behalf this tier was purchased through the merchant of record ("you"). The person completing the purchase confirms that they may accept this Agreement for that entity.

Gumroad, Inc. acts as merchant of record and sells the download to you. This Agreement is between you and the Licensor and governs what you may do with the Licensed Material.

## 2. Definitions

- **Licensed Material**: the event tables in `data/events/`, the exclusions file `data/excluded_events.csv`, the aggregate tables, monthly series and verdict files in `data/benchmarks/`, and the Documentation, including their selection, labels, classifications, structure and computed statistics.
- **Code**: the loader, schema validator, event-study engine, price-provider interface, tests and sample notebook in `code/`.
- **Documentation**: the README, data dictionary, methodology, provenance, known-limitations, risk-notice and changelog files.
- **Internal Users**: your employees, and contractors working on your behalf under a written confidentiality obligation, while they work for you.
- **Named Product**: the one external product or publication you name to the Licensor in writing at or after purchase, for example a named software product, website, app, newsletter, course or book, produced and offered by you under your own name or brand.
- **Derived Results**: anything you produce using the Licensed Material that is not the event tables themselves or a substantial part of them, for example statistics, charts, models, backtests, screens, reports or dashboards.

## 3. The Code is MIT licensed and is not restricted here

The Code is published under the MIT Licence, including publicly on GitHub, and the MIT text is in `code/LICENSE`. Nothing in this Agreement restricts, conditions or narrows your rights in the Code. You may use, modify, keep and redistribute the Code under the MIT terms, inside the Named Product and for any other purpose.

This Agreement licenses the **data and the Documentation** only: the event tables, the exclusions file, the aggregate tables, the monthly series, the verdict files and the written documentation.

## 4. What you may do

Subject to this Agreement and payment of the fee, the Licensor grants you a non-exclusive, non-transferable, worldwide, perpetual licence, for **one legal entity**, to:

a) do everything the Organization / Commercial licence allows: internal use by any number of Internal Users with no seat counting, internal models, reports and dashboards, external publication of aggregates, charts and up to 25 example event rows per publication, and use of derived insights in consulting and research;
b) use the Licensed Material in **one Named Product**;
c) display individual events in the Named Product in human-readable form;
d) display cumulatively **at most 100 event rows or 10 % of the dataset, whichever is lower**, across the whole life of the Named Product;
e) show those rows **embedded only**, inside the Named Product, without any bulk download;
f) make backup copies and copies for development and testing.

Internal Users delete their copies when their work for you ends.

## 5. What you may not do

You may not:

a) resell or offer the Licensed Material, or a substantial part of it, stand-alone, that is as a dataset, file download, data product or database whose substance is the data itself, whether or not renamed, re-sorted, reformatted or lightly edited;
b) allow full or near-full reconstruction of the dataset from the Named Product, whether by display, export, scraping-friendly presentation or repeated queries;
c) offer the data through an API or any machine-readable bulk export;
d) sublicense the data to other companies, publishers, platforms, data vendors or resellers;
e) use the Licensed Material to train a competing dataset product, or to train, fine-tune or prompt a model whose purpose is to reproduce the dataset or a substitute for it;
f) give access to affiliated companies. Parent companies, subsidiaries and sister companies are separate entities and need their own licence;
g) exceed the display limits in section 4 d) and e), or use the data in a second product or publication;
h) remove or alter copyright, licence or attribution notices, or present the Licensed Material or the benchmark results as your own work without the attribution in section 6.

**A real API, a data feed or OEM redistribution is not covered by this licence and is available as a separate licence on request.**

Facts are not owned by anyone. Nothing here stops you from collecting Form 8-K filings yourself from SEC EDGAR and building your own table. These restrictions apply to the Licensor's compiled, labelled and structured tables and statistics, not to the underlying public filings.

## 6. Attribution

The Named Product and every publication that shows benchmark results, event rows or statements that events come from the dataset carries:

> Event data: SEC 8-K Event Dataset v1 (aiamond, Lennart Schreiber), derived from SEC EDGAR Form 8-K filings. https://aiamond.com

Where space is limited, for example in a chart footnote, a video description or an "About the data" page, "Source: aiamond SEC 8-K Event Dataset v1" is acceptable. Purely internal use needs no attribution.

## 7. Ownership

The Licensor owns the database and the Documentation, including the selection, cleaning, labelling, deduplication and structuring of the tables and the statistics computed from them, and retains all rights not expressly granted here. The Code is owned by the Licensor and licensed to everyone under the MIT Licence as stated in section 3.

## 8. Third-party data notice

The events derive from public Form 8-K filings retrieved through SEC EDGAR. Those filings are works of the United States government and are in the public domain.

Index membership flags come from filtering the events against public index-change information. **No membership table is redistributed**; index names are used descriptively and not as a licensed index product.

The aggregate statistics were computed by the Licensor from historical adjusted closing prices of a third-party source whose terms do not permit redistribution of that source's data. **Therefore the Licensed Material contains no prices and no per-trade rows**, and the price series cannot be reconstructed from it. The aggregates are provided as the Licensor's own derived statistics and as methodological example output. The provenance of every column is documented in `docs/PROVENANCE.md`. The Licensor grants no right in any third-party price data and cannot do so.

**You are responsible for your own price source and for complying with its licence terms**, including terms for commercial use and for publication, when you recompute, extend or publish anything based on prices.

## 9. No investment advice

The Licensed Material is historical research material. It is not investment advice, not a recommendation to buy or sell any security, not a trading signal, and not an offer or solicitation. The results describe what happened in the past under stated assumptions and imply no promise about future returns. The Licensor is not a registered investment adviser in any jurisdiction. You are responsible for how you present the results in the Named Product and for any financial-promotion, disclosure or advice rules that apply in the countries you address.

## 10. Warranties and liability

To the maximum extent permitted by law, the Licensed Material is provided "as is" and without warranties of accuracy, completeness, fitness for a particular purpose, non-infringement, investment performance or uninterrupted availability. In particular the event tables can contain classification errors, missed filings and ticker-mapping errors, and the statistics depend on the price source used and on the limitations described in the Documentation.

The Licensor is not liable for indirect, incidental, consequential, special or lost-profit damages, including losses of your users and customers. The Licensor's aggregate liability arising from the Licensed Material is limited to the amount paid for this licence.

These limitations do not apply where liability cannot lawfully be excluded or limited, including liability for intent, fraud, wilful misconduct, gross negligence, death or personal injury, and mandatory consumer protection rights.

## 11. Payment, delivery, refunds and withdrawal

Gumroad, as merchant of record, administers payment, delivery, refunds and any statutory withdrawal process under the terms presented at checkout. Nothing in this EULA limits any mandatory consumer rights. If this EULA conflicts with Gumroad's checkout terms regarding payment, refunds or withdrawal, those checkout terms control; this EULA continues to govern the licence and permitted use of the data.

## 12. No support, no updates

The fee covers this version only. There is no entitlement to support, to a service level, or to updates, corrections, new event classes or new versions; these may be offered separately. The Licensor may answer questions about documented standard cases at its discretion.

## 13. Term and termination

This licence runs indefinitely from purchase. The Licensor may terminate the licence for a material breach that is not cured within 14 days after notice, except that deliberate unauthorised redistribution may result in immediate termination.

On termination you delete all copies of the Licensed Material and remove the displayed event rows from the Named Product. The redistribution bans in section 5 survive termination, as do sections 6 to 10 and 14. Copies of a publication already delivered to readers, and Derived Results created in compliance with this Agreement before termination, may remain.

## 14. Governing law and jurisdiction

This Agreement is governed by the laws of Spain, without depriving consumers of mandatory protections available under the law of their habitual residence. For business users, the courts at the Licensor's registered place of business in Spain have exclusive jurisdiction. Consumers may bring claims in any court available to them under mandatory law.

## 15. Severability and entire agreement

If any provision is invalid or unenforceable, the rest remains in force and the provision is replaced by a valid one that comes closest to its purpose.

This Agreement, the MIT Licence for the Code, and the merchant of record's checkout terms are the entire agreement about the Licensed Material and replace earlier statements. Changes require written form. Listing text and Documentation describe the product; they do not add rights beyond this Agreement. Purchase-order terms or other standard terms of yours do not apply.

## 16. Version

EULA Product / Publication, v1, 2026-09-18. The version you accepted at purchase applies to your copy; later versions apply only to later purchases.
