# Which licence applies to you

The SEC 8-K Event Dataset is sold in three tiers. **The tier you bought at checkout is the one that
applies**; your Gumroad receipt names it. Each file below is the full agreement for that tier.

| Gumroad variant | Price | File |
|---|---:|---|
| Individual / Academic | USD 79 | [EULA-individual.md](EULA-individual.md) |
| Organization / Commercial | USD 249 | [EULA-organization.md](EULA-organization.md) |
| Product / Publication | USD 599 | [EULA-product.md](EULA-product.md) |
| Individual / Academic, **Starter edition** (one class: Item 2.06) — separate product | USD 29 | [EULA-individual-starter.md](EULA-individual-starter.md) |

Prices are net of any VAT or sales tax the merchant of record adds at checkout.

## The code is MIT, the data is licensed

The Python code in `code/` (loader, schema validator, event-study engine, price-provider interface,
tests, sample notebook) is under the **MIT Licence**, published publicly on GitHub, and is
**not restricted by any EULA**. Its text is in [`../code/LICENSE`](../code/LICENSE). Use, modify and
redistribute it freely, commercially or not.

The EULAs license the **data and the documentation**: the event tables in `data/events/`, the
exclusions file, the aggregate tables, monthly series and verdict files in `data/benchmarks/`, and
the written docs.

## What each tier may do

| | Individual / Academic (79) | Organization / Commercial (249) | Product / Publication (599) |
|---|---|---|---|
| **Who may use the data** | one named natural person | one legal entity, any number of employees and bound contractors, no seat counting | one legal entity, same as Organization |
| **Internal use** | private, academic and your own commercial analysis | internal models, reports and dashboards | everything Organization allows |
| **External publication** | aggregates, charts, conclusions and short examples; reproduction package for a journal without the full dataset | aggregates, charts and up to 25 example event rows per publication; derived insights in consulting and research | plus one named external product or publication: human-readable display of individual events, cumulatively at most 100 rows or 10 % of the dataset, whichever is lower, embedded only |
| **Sharing with others** | derived results with co-authors, who need no licence of their own as long as they do not receive the full data | no customer downloads of the raw data, no access for parent, subsidiary or sister companies | no sublicensing, no resale, no supply to other publishers or vendors |
| **Never allowed** | passing on the raw data, shared lab or team access, making a substantial part of the event rows public | API, bulk export or data feed; use as a substitute for the dataset itself | stand-alone resale, full or near-full reconstruction, API or machine-readable bulk export, training a competing dataset product |

A real API, a data feed or OEM redistribution is not covered by any of these tiers and is available as
a separate licence on request.

All tiers require attribution to aiamond (https://aiamond.com), carry no investment advice and no
promise of returns, leave you responsible for your own price source, and include no support, service
level or update entitlement. Payment, delivery, refunds and any statutory withdrawal process are
handled by Gumroad as merchant of record under the terms shown at checkout.

**These drafts have not yet been reviewed by a lawyer** (state 2026-09-18).
