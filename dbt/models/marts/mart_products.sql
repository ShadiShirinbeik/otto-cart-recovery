-- one row per product: how often it was clicked, added to cart and ordered

select
    product_id,
    count(*) filter (where event_type = 'clicks') as n_clicks,
    count(*) filter (where event_type = 'carts') as n_carts,
    count(*) filter (where event_type = 'orders') as n_orders,
    round(
        count(*) filter (where event_type = 'orders')::numeric
        / nullif(count(*) filter (where event_type = 'carts'), 0),
        3
    ) as cart_to_order_rate
from {{ ref('stg_events') }}
group by product_id
