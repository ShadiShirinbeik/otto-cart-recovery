# From Click to Order: Recovering Abandoned Carts at OTTO

Cart abandonment analysis on real OTTO e-commerce data (12.9M sessions): funnel KPIs, buyer types, purchase timing and A/B test sizing to build a cart recovery plan.

**Tools:** Python (pandas, statsmodels, Seaborn, Plotly) · SQL · PostgreSQL · dbt · Tableau

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
10. [Acknowledgements](#10-acknowledgements)

---

## 1. Business problem

**Background.** On average, about 70% of online shopping carts are abandoned ([Baymard Institute](https://baymard.com/research/cart-abandonment-rate)). These users already wanted to buy, so every abandoned cart is a lost order.

**Goal.** Help an online shop get more orders from the visitors it already has, by recovering abandoned carts, instead of spending more on ads to get new visitors.

**Impact.** The result is a data-backed cart recovery plan that answers:
- How many orders are being lost?
- Which users should be targeted?
- When should they be contacted?
- How can the effect be proven with an A/B test?

## 2. KPIs

| Type | KPI | Definition |
|---|---|---|
| Main | Cart abandonment rate | Share of users with a cart add and no order (see [data rules](#data-rules)) |
| Main | Order conversion rate | Share of all users that place at least one order |
| Outcome | Recoverable orders | Extra buyers if X% of abandoned carts were recovered |
| Supporting | Click-to-cart rate | Share of users who add something to the cart |
| Supporting | Time to purchase | Time from first cart add to first order |
| Supporting | Cart adds per user | How many times a user added something to the cart |
| Supporting | Conversion rate by weekday and hour | Share of orders by time |
| Supporting | Buyer type share | Share of users in each buyer type (browser, abandoner, quick / same-day / slow buyer) |

**Success** means a measured baseline for every KPI, a clear estimate of recoverable orders, and a reminder plan (who, when, test size) backed by statistical tests.

## 3. Business questions

| # | Question | KPI that answers it | Method |
|---|---|---|---|
| Q1 | How many customers do we lose, and how many orders could we win back? | Cart abandonment rate, order conversion rate, recoverable orders | Funnel, confidence interval, recovery scenarios (e.g. 5%, 10%, 20%) |
| Q2 | Who should we contact? | Buyer type share, cart adds per user | Rule-based buyer types, behaviour comparison |
| Q3 | When should we contact them? | Time to purchase, conversion rate by weekday and hour | Time-to-purchase distribution, two-proportion z-test |
| Q4 | How do we test if it works? | Required sample size per group | Sample size calculation, samples vs. full data |

## 4. Data source

| Item | Details |
|---|---|
| Dataset | OTTO Recommender Systems Dataset, published by OTTO (German online retailer) |
| Official repository | https://github.com/otto-de/recsys-dataset |
| Download | Kaggle: https://www.kaggle.com/datasets/otto/recsys-dataset |
| Licence | CC BY 4.0 (free to use with attribution) |
| Type | Real event data (not synthetic), 1–28 August 2022 |
| Size | 12,899,779 sessions, 216,716,096 events (clicks, cart adds, orders) |
| File used | `otto-recsys-train.jsonl` (~11 GB) |

**Columns:** `session` (anonymised user ID), `aid` (anonymised product ID), `ts` (Unix timestamp in milliseconds), `type` (`clicks`, `carts`, `orders`).

**Sessions.** A session holds all activity of one anonymous user in the 4 weeks. In this project, one session = one user. All IDs are anonymised; there is no personal data.

### Sample

- **What:** 1,000,000 random sessions (about 7.8%), with all events of each session, so a user's cart and order stay together. Fixed seed, so the sample can be repeated.
- **Size:** 16,857,546 events after cleaning, as a flat table (one row per event).
- **Check:** the share of clicks, carts and orders and the spread over all 28 days are almost the same as in the full data.
- **Used for:** PostgreSQL, dbt, the analysis and the dashboard. The full data is used for the overall totals and to check the sample.

### Data rules

- **Duplicates:** rows with the same session, product, type and millisecond are removed (0.16%, mostly orders).
- **Late carts:** users who added to the cart on August 27–28 and did not order are not counted as abandoners, because they may have ordered after the data period (`late_cart`).
- **Orders without a cart:** users who ordered but have no cart add in the data period (the item was added before August 1st) are left out of the abandonment and timing analysis (`other`).
- **Sessions that start with a cart or order:** the click happened before August 1st. They are kept, but left out of the time-to-purchase analysis.

**Buyer types** (column `buyer_type` in `mart_sessions`):

| Buyer type | Rule |
|---|---|
| browser | No cart add and no order |
| abandoner | Cart add, but no order |
| quick_buyer | Ordered less than 1 hour after the first cart add |
| same_day_buyer | Ordered 1–24 hours after the first cart add |
| slow_buyer | Ordered more than 24 hours after the first cart add |
| late_cart | Cart add on August 27–28, no order (excluded) |
| other | Order without a cart add in the data period (excluded) |

## 5. Data pipeline and lineage

```
Kaggle API → raw JSONL → 1M-session sample → clean events → PostgreSQL → dbt models → Python analysis → Tableau dashboard
```

| Stage | Tool | Input | Output | Location |
|---|---|---|---|---|
| Collect | Kaggle API | Kaggle dataset | `otto-recsys-train.jsonl` | `data/raw/` |
| Explore | Python (`01_data_overview.ipynb`) | Raw JSONL | Totals for the full data | `data/processed/` |
| Sample | Python (`src/make_sample.py`) | Raw JSONL | 1M random sessions as a flat table (`events_sample_raw.parquet`) | `data/processed/` |
| Clean | Python (`02_clean_sample.ipynb`) | Sample | Duplicates removed (`events_clean.parquet`, `events_clean.csv`) | `data/processed/` |
| Store | PostgreSQL | `events_clean.csv` | `otto.raw_events` table | PostgreSQL, schema `otto` |
| Transform | dbt | `otto.raw_events` | `stg_events` → `prep_sessions` → `mart_sessions` | `dbt/` |
| Analyze | Python (`03_cart_abandonment.ipynb`, `04_who_to_contact.ipynb`) | dbt marts | Tests and charts | `notebooks/`, `docs/figures/` |
| Visualize | Tableau, Seaborn, Plotly | dbt marts | Dashboard and charts | `dashboard/` |

### dbt models

| Layer | Model | One row per | What it does |
|---|---|---|---|
| Staging | `stg_events` | event | Renames columns, adds Berlin time. The raw table stays unchanged. |
| Prep | `prep_sessions` | user | Counts clicks, cart adds, orders, products and active days; keeps the first click, cart and order time |
| Mart | `mart_sessions` | user | Final features: cart abandonment, hours from cart to order, order weekday and hour, buyer type, data-rule flags |

dbt tests check that every user appears only once in the mart.

## 6. Repository structure

```
otto-cart-recovery/
├── data/            # not committed (see .gitignore)
│   ├── raw/         # original Kaggle file
│   └── processed/   # sample and clean data
├── notebooks/       # exploration and analysis
├── src/             # Python scripts (sampling)
├── sql/             # SQL to create the raw table
├── dbt/             # dbt project
├── dashboard/       # Tableau workbook and screenshots
├── docs/            # presentation and extra documentation
└── README.md
```

## 7. How to reproduce

**Prerequisites:** Python 3.10+, a PostgreSQL database, a Kaggle account, at least 20 GB of free disk space.

1. Clone the repository and create the data folders:
   ```bash
   git clone https://github.com/ShadiShirinbeik/otto-cart-recovery.git
   cd otto-cart-recovery
   mkdir -p data/raw data/processed
   ```
2. Install the Python packages:
   ```bash
   pip install pandas pyarrow seaborn plotly statsmodels jupyter kaggle dbt-postgres sqlalchemy psycopg2-binary python-dotenv
   ```
3. Download the data with the Kaggle API (requires `kaggle.json` from your Kaggle account settings):
   ```bash
   kaggle datasets download -d otto/recsys-dataset -p data/raw --unzip
   ```
4. Run `notebooks/01_data_overview.ipynb` to count the full data (about 10–15 minutes).
5. Create the sample, then run `notebooks/02_clean_sample.ipynb` to clean it and export `events_clean.csv`:
   ```bash
   python src/make_sample.py
   ```
6. Load the clean data into PostgreSQL: run `sql/01_create_raw_events.sql`, then import `data/processed/events_clean.csv` into `otto.raw_events` (for example with DBeaver's Import Data).
7. Create `dbt/profiles.yml` with your database connection (this file is not committed):
   ```yaml
   otto:
     target: dev
     outputs:
       dev:
         type: postgres
         host: YOUR_HOST
         port: 5432
         user: YOUR_USER
         password: YOUR_PASSWORD
         dbname: YOUR_DATABASE
         schema: otto
         threads: 4
   ```
8. Build and test the dbt models:
   ```bash
   cd dbt
   dbt run
   dbt test
   ```
9. Create a `.env` file in the project folder with the same connection (not committed), then run notebooks 03 and 04. They download the dbt tables once and save the charts in `docs/figures/`:
   ```
   POSTGRES_USER=YOUR_USER
   POSTGRES_PASS=YOUR_PASSWORD
   POSTGRES_HOST=YOUR_HOST
   POSTGRES_PORT=5432
   POSTGRES_DB=YOUR_DATABASE
   ```

## 8. Findings

## 9. Limitations

- No prices: results are measured in orders and buyers, not euros.
- No product names, categories, device or marketing-channel data.
- Only 4 weeks of history, so no seasonality or long-term behaviour.
- A real person using two devices may appear as two sessions.
- Cart abandonment is measured per user over 4 weeks, so it is not directly comparable with per-visit benchmarks.

## 10. Acknowledgements

Data: OTTO Recommender Systems Dataset by OTTO (GmbH & Co KG), licensed under CC BY 4.0. https://github.com/otto-de/recsys-dataset
