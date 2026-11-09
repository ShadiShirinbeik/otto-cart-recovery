-- one row per session: counts and the key times

select
    session_id,

    count(*) filter (where event_type = 'clicks') as n_clicks,
    count(*) filter (where event_type = 'carts') as n_carts,
    count(*) filter (where event_type = 'orders') as n_orders,
    count(distinct product_id) as n_products,
    count(distinct event_date) as active_days,

    min(event_time) as first_event_time,
    max(event_time) as last_event_time,
    min(event_time) filter (where event_type = 'clicks') as first_click_time,
    min(event_time) filter (where event_type = 'carts') as first_cart_time,
    min(event_time) filter (where event_type = 'orders') as first_order_time

from {{ ref('stg_events') }}
group by session_id
