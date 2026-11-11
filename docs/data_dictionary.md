# Data Dictionary

All tables used in the project, in the order of the pipeline. Times are in Berlin time unless stated otherwise.

## 1. Raw data – `data/raw/otto-recsys-train.jsonl`

Source: OTTO Recommender Systems Dataset (Kaggle, CC BY 4.0). One line per user, 12,899,779 lines, August 1–28, 2022.

| Field | Type | Meaning | Example |
|---|---|---|---|
| `session` | integer | Anonymous user ID | `0` |
| `events` | list | All actions of this user, sorted by time | – |
| `events.aid` | integer | Anonymous product ID | `1517085` |
| `events.ts` | integer | Time of the action, Unix time in milliseconds (UTC) | `1659304800025` |
| `events.type` | text | Type of action: `clicks`, `carts` (added to cart) or `orders` | `clicks` |

## 2. Clean sample – `data/processed/events_clean.csv` → PostgreSQL `otto.raw_events`

1M random users from the raw file, one row per event (16,857,546 rows), exact duplicates removed.

| Column | Type | Meaning |
|---|---|---|
| `session` | integer | Anonymous user ID |
| `aid` | integer | Anonymous product ID |
| `ts` | integer | Time in milliseconds (UTC) |
| `type` | text | `clicks`, `carts` or `orders` |

## 3. dbt staging – `otto.stg_events`

Same rows as `raw_events`, with clear names and Berlin time.

| Column | Type | Meaning |
|---|---|---|
| `session_id` | integer | Anonymous user ID |
| `product_id` | integer | Anonymous product ID |
| `event_type` | text | `clicks`, `carts` or `orders` |
| `event_time` | timestamp | Time of the event (Berlin) |
| `event_date` | date | Day of the event |

## 4. dbt prep – `otto.prep_sessions`

Groups all events of a user into **one row per user**. It only counts actions and keeps the key times; the mart then turns these into features like `is_abandoned` or `hours_cart_to_order`.

| Column | Type | Meaning |
|---|---|---|
| `session_id` | integer | Anonymous user ID |
| `n_clicks` | integer | Number of clicks |
| `n_carts` | integer | Number of cart adds |
| `n_orders` | integer | Number of ordered items |
| `n_products` | integer | Number of different products |
| `active_days` | integer | Number of different days with activity |
| `first_event_time` | timestamp | Time of the user's first event |
| `last_event_time` | timestamp | Time of the user's last event |
| `first_click_time` | timestamp | Time of the first click (empty if no click) |
| `first_cart_time` | timestamp | Time of the first cart add (empty if no cart) |
| `first_order_time` | timestamp | Time of the first order (empty if no order) |

**Example:** a user with 4 events (2 clicks and a cart add on Aug 3, an order on Aug 5) becomes one row:

| session_id | n_clicks | n_carts | n_orders | active_days | first_cart_time | first_order_time |
|---|---|---|---|---|---|---|
| 7 | 2 | 1 | 1 | 2 | 2022-08-03 10:06 | 2022-08-05 18:30 |

## 5. dbt mart – `otto.mart_sessions` (main analysis table)

One row per user (1,000,000 rows). All notebooks from 03 on and the Tableau story use this table.

| Column | Type | Meaning | Empty when |
|---|---|---|---|
| `session_id` | integer | Anonymous user ID | – |
| `start_date` | date | Day of the user's first event | – |
| `start_weekday` | text | Weekday of the first event (`Monday` … `Sunday`) | – |
| `start_hour` | integer | Hour of the first event (0–23) | – |
| `n_clicks` | integer | Number of clicks | – |
| `n_carts` | integer | Number of cart adds | – |
| `n_orders` | integer | Number of ordered items | – |
| `n_products` | integer | Number of different products the user interacted with | – |
| `active_days` | integer | Number of different days with activity (1–28) | – |
| `duration_hours` | decimal | Hours from the first to the last event | – |
| `has_cart` | true/false | Added at least one item to the cart | – |
| `has_order` | true/false | Placed at least one order | – |
| `is_abandoned` | true/false | Added to cart but never ordered | – |
| `hours_cart_to_order` | decimal | Hours from the first cart add to the first order | the user did not order after a cart add |
| `order_weekday` | text | Weekday of the first order | no order |
| `order_hour` | integer | Hour of the first order (0–23) | no order |
| `is_weekend_order` | true/false | First order on Saturday or Sunday | no order |
| `starts_with_cart_or_order` | true/false | First event is a cart add or order (the click happened before August 1st) | – |
| `cart_in_last_days` | true/false | First cart add on August 27–28 (the order may come after the data period) | no cart |
| `buyer_type` | text | User group, see below | – |

**Buyer types**

| Value | Rule |
|---|---|
| `browser` | No cart add and no order |
| `abandoner` | Cart add, but no order |
| `quick_buyer` | Ordered less than 1 hour after the first cart add |
| `same_day_buyer` | Ordered 1–24 hours after the first cart add |
| `slow_buyer` | Ordered more than 24 hours after the first cart add |
| `late_cart` | Cart add on August 27–28 and no order (left out of the analysis) |
| `other` | Order without a cart add in the data period (left out of the analysis) |


