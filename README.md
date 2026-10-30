# From Click to Order: Recovering Abandoned Carts at OTTO

Cart abandonment analysis on real OTTO e-commerce data (12.9M sessions): funnel KPIs, user segments, purchase timing and A/B test sizing to build a cart recovery plan.

**Tools:** Python (pandas, NumPy, SciPy, statsmodels, scikit-learn, Matplotlib, Seaborn) · SQL · PostgreSQL · dbt · Tableau

---

## Contents
1. [Business problem](#1-business-problem)
2. [KPIs](#2-kpis)
3. [Business questions](#3-business-questions)
4. [Data source](#4-data-source)
5. [Data pipeline and lineage](#5-data-pipeline-and-lineage)
6. [Repository structure](#6-repository-structure)
7. [How to reproduce](#7-how-to-reproduce)
8. [Findings](#8-findings)
9. [Limitations](#9-limitations)
10. [Project timeline](#10-project-timeline)
11. [Acknowledgements](#11-acknowledgements)

---

## 1. Business problem

**Background.** Online shops lose most of their potential buyers at the cart stage. On average, about 70% of online shopping carts are abandoned ([Baymard Institute](https://baymard.com/research/cart-abandonment-rate)). These users have already shown purchase intent, so every abandoned cart is a lost order.

**Goal.** Help an online shop get more orders from the visitors it already has, by recovering abandoned carts.

A shop's revenue roughly equals *visitors × conversion rate × basket value*. Getting more visitors costs money (advertising). This project focuses on conversion: turning more existing visitors into buyers.

**Impact.** The result is a data-backed cart recovery plan that answers:
- How many orders are being lost?
- Which users should be targeted?
- When should they be contacted?
- How can the effect be proven with an A/B test?

## 2. KPIs

| Type | KPI | Definition |
|---|---|---|
| Main | Cart abandonment rate | Share of sessions with at least one cart add and no order |
| Main | Order conversion rate | Share of all sessions that place at least one order |
| Outcome | Recoverable orders | Extra orders if X% of abandoned carts were recovered |
| Supporting | Click-to-cart rate | Share of sessions with a click that also add to cart |
| Supporting | Cart-to-order rate | Share of sessions with a cart add that also order |
| Supporting | Time to purchase | Time from first cart add to order |
| Supporting | Active days per session | Number of distinct days with activity |
| Supporting | Conversion rate by weekday and hour | Share of sessions that order, by time |
| Supporting | Items per order | Average number of products in an ordering session (basket size) |
| Supporting | Product cart-to-order rate | For each product, share of cart adds that end in an order |
| Supporting | Conversion rate by segment | Order rate for each user group found with k-means |

**Success** means a measured baseline for every KPI, a clear estimate of recoverable orders, and a reminder plan (who, when, test size) backed by statistical tests.

## 3. Business questions

| # | Question | KPI that answers it | Method |
|---|---|---|---|
| Q1 | How many customers do we lose, and how many orders could we win back? | Cart abandonment rate, order conversion rate, recoverable orders | Funnel, confidence interval, recovery scenarios (e.g. 5%, 10%, 20%) |
| Q2 | Who should we contact? | Active days per session, conversion rate by segment | Group comparisons, k-means segments |
| Q3 | When should we contact them? | Time to purchase, conversion rate by weekday and hour | Time-to-purchase distribution, two-proportion z-test |
| Q4 | How do we test if it works? | Required sample size per group | Sample size calculation, samples vs. full data |
| Bonus | Which products are abandoned most? | Product cart-to-order rate | Products with many cart adds but few orders |

## 4. Data source

| Item | Details |
|---|---|
| Dataset | OTTO Recommender Systems Dataset |
| Publisher | OTTO (German online retailer) |
| Official repository | https://github.com/otto-de/recsys-dataset |
| Download | Kaggle: https://www.kaggle.com/datasets/otto/recsys-dataset |
| Licence | CC BY 4.0 (free to use with attribution) |
| Type | Real event data (not synthetic), 4 weeks of 2022 |
| Size | ~12.9M sessions, ~216M events (clicks, cart adds, orders) |
| File used | `otto-recsys-train.jsonl` (~11 GB). The test file covers a different week and is not used. |

**Columns:** `session` (anonymised user ID), `aid` (anonymised product ID), `ts` (Unix timestamp in milliseconds), `type` (`clicks`, `carts`, `orders`).

**Ethics.** All user and product IDs are anonymised. The dataset contains no personal data.

### Sample

- **What:** 1,000,000 sessions picked at random from the 12.9M (about 7.8%), with all events of each session, so a user's cart and order stay together. Fixed seed, so the same sample comes out every time.
- **Size:** 16,857,546 events after cleaning (0.16% duplicates removed).
- **Columns:** `session`, `aid`, `ts`, `type` (the Parquet file also has `event_time` in Berlin time).
- **Difference from the full data:** a flat table (one row per event) instead of nested JSON, 253 MB instead of 11 GB, no duplicates. The share of clicks, carts and orders is almost the same as in the full data.
- **Used for:** PostgreSQL, dbt and almost all analysis and the dashboard. The full data is used only for the overall totals and to check the sample (Q4).

## 5. Data pipeline and lineage

```
Kaggle API → raw JSONL → 1M-session sample → clean events → PostgreSQL → dbt models → Python analysis → Tableau dashboard
```

| Stage | Tool | Input | Output | Location |
|---|---|---|---|---|
| Collect | Kaggle API | Kaggle dataset | `otto-recsys-train.jsonl` | `data/raw/` |
| Sample | Python (`src/make_sample.py`) | Raw JSONL | 1M random sessions as a flat table (`events_sample_raw.parquet`) | `data/processed/` |
| Clean | Python / pandas (`02_clean_sample.ipynb`) | Sample | Duplicates removed (`events_clean.parquet`, `events_clean.csv`) | `data/processed/` |
| Store | PostgreSQL | `events_clean.csv` | `raw.events` table | Local database |
| Transform | dbt | `raw.events` | Staging, session-level and daily KPI models | `dbt/` |
| Analyze | Python (statsmodels, scikit-learn) | dbt models | Tests, models, charts | `notebooks/` |
| Visualize | Tableau, Seaborn | Analysis results | Dashboard and charts | `dashboard/` |

*Details for each step will be added as it is completed.*

## 6. Repository structure

```
otto-cart-recovery/
├── data/            # not committed (see .gitignore)
│   ├── raw/         # original Kaggle file
│   └── processed/   # cleaned and sampled data
├── notebooks/       # exploration and analysis
├── src/             # reusable Python scripts
├── sql/             # SQL queries
├── dbt/             # dbt project
├── dashboard/       # Tableau workbook and screenshots
├── docs/            # presentation and extra documentation
└── README.md
```

## 7. How to reproduce

**Prerequisites:** Python 3.10+, PostgreSQL, dbt-postgres, a Kaggle account, at least 20 GB of free disk space.

1. Clone the repository:
   ```bash
   git clone https://github.com/ShadiShirinbeik/otto-cart-recovery.git
   cd otto-cart-recovery
   ```
2. Create the data folders:
   ```bash
   mkdir -p data/raw data/processed
   ```
3. Download the data with the Kaggle API (requires `kaggle.json` from your Kaggle account settings):
   ```bash
   pip install kaggle
   kaggle datasets download -d otto/recsys-dataset -p data/raw --unzip
   ```
4. *Further steps (Python environment, cleaning, database load, dbt) will be added as they are built.*

## 8. Findings

*Coming in weeks 2–3.*

## 9. Limitations

- No prices: results are measured in orders, not euros.
- No product names, categories, device or marketing-channel data.
- Only 4 weeks of history, so no seasonality or long-term behaviour.
- Some sessions start with a cart add or order (items added before the data period); these are excluded from timing analysis.
- Carts from the last days may lead to orders after the data period; these are excluded from abandonment rates.

## 10. Project timeline

- [ ] **Week 1:** Project definition, data pipeline (cleaning, PostgreSQL, dbt staging)
- [ ] **Week 2:** Q1 (size of the problem), Q4 (A/B test sizing)
- [ ] **Week 3:** Q2 (targeting), Q3 (timing), high-hesitation products
- [ ] **Week 4:** Tableau dashboard, cart recovery plan, final presentation

## 11. Acknowledgements

Data: OTTO Recommender Systems Dataset by OTTO (GmbH & Co KG), licensed under CC BY 4.0. https://github.com/otto-de/recsys-dataset
