# Stand-Up 1 – From Click to Order: Recovering Abandoned Carts at OTTO

October 30, 2026

## Main goal

Help an online shop get more orders from the visitors it already has, by recovering abandoned carts.
About 70% of online carts are abandoned on average ([Baymard Institute](https://baymard.com/research/cart-abandonment-rate)), and these users already wanted to buy.
The result will be a cart recovery plan: how many orders are lost, who to target, when to contact them, and how to test it.


## KPIs

- **Main:** cart abandonment rate (sessions with a cart add but no order)
- **Outcome:** recoverable orders (extra orders if X% of abandoned carts come back)
- **Supporting:** click-to-cart rate, cart-to-order rate, time to purchase, active days per session, conversion by weekday and hour

## Why the OTTO dataset

- Real data from a German company (OTTO), from 2022, not synthetic and not a classroom dataset
- Large: 12.9M sessions and 216M events, published officially by OTTO under a CC BY 4.0 licence
- It has exactly what the goal needs: every click, cart add and order with an exact timestamp
- Alternatives were older, not German, offline, or partly fake (obfuscated) data

## What about missing categories?

- The questions are about **behaviour and timing** (who abandons carts, when, how many orders are lost), not about what is bought, so categories are not needed
- Products can still be compared by their ID
- What is lost: category comparisons and revenue in euros. This is stated openly as a limitation, and results are measured in orders
- Datasets with categories were older, not German, or obfuscated, so they would bring other problems

## The data is ready

```
data/raw/otto-recsys-train.jsonl           11 GB    full dataset
data/processed/events_sample_raw.parquet   159 MB   1M-session sample
data/processed/events_clean.csv            599 MB   clean sample for PostgreSQL
```

First 10 rows of the clean events table:

```
session  aid       ts              type    event_time (Berlin)
1        424964    1659304800025   carts   2022-08-01 00:00:00
1        1492293   1659304852871   clicks  2022-08-01 00:00:52
1        1492293   1659304863627   carts   2022-08-01 00:01:03
1        910862    1659304891923   clicks  2022-08-01 00:01:31
1        910862    1659304900209   carts   2022-08-01 00:01:40
1        1491172   1659385939248   clicks  2022-08-01 22:32:19
1        1491172   1659385945915   carts   2022-08-01 22:32:25
1        424964    1659385993848   clicks  2022-08-01 22:33:13
1        1515526   1659386025990   clicks  2022-08-01 22:33:45
1        440486    1659473014870   clicks  2022-08-02 22:43:34
```

This session starts with a cart add.




---

## What I did

**GitHub setup**
Created the repository with folders for notebooks, src, sql, dbt, dashboard and docs.
The data folder is in `.gitignore`, so the 11 GB file is not uploaded; the README explains how to download it.
The README already covers the problem, KPIs, data source, pipeline and how to reproduce.

**Pipeline draft**
Kaggle → raw JSON file → Python cleaning → 1M-session sample → PostgreSQL → dbt models → Python analysis → Seaborn charts and Tableau dashboard → README and presentation.

**Notebook 01 – Data overview**
Looks at a few sessions to understand the JSON structure (one line = one session with a list of events).
Reads the full 11 GB file line by line and counts sessions and events by type.
Result: 12,899,779 sessions and 216.7M events, matching OTTO's official numbers. 29.5% of sessions add to cart, but only 12.6% order.

**Sampling script (`src/make_sample.py`)**
Picks 1M sessions at random (simple random sampling, fixed seed so the same sample comes out every time).
Whole sessions are kept with all their events, so a user's cart and order always stay together.
The nested JSON is turned into a flat table: session, product, timestamp, event type.

**Notebook 02 – Cleaning**
Converts timestamps to Berlin time and checks for missing values (none) and the date range.
Compares the sample with the full data: the share of clicks, carts and orders is almost identical, so the sample is representative.
Removes 0.16% exact duplicate rows and saves the clean table (16.9M events) for PostgreSQL.

## Next steps

Load the clean sample into PostgreSQL, build the first dbt models, and start the funnel and cart abandonment analysis.
