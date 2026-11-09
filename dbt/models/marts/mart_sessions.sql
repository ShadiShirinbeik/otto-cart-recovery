-- final session table: one row per session, used for the analysis and Tableau

with sessions as (
    select * from {{ ref('prep_sessions') }}
)

select
    session_id,

    -- when the session started
    first_event_time::date as start_date,
    trim(to_char(first_event_time, 'Day')) as start_weekday,
    extract(hour from first_event_time)::int as start_hour,

    -- behaviour
    n_clicks,
    n_carts,
    n_orders,
    n_products,
    active_days,
    round((extract(epoch from last_event_time - first_event_time) / 3600)::numeric, 2) as duration_hours,

    -- funnel
    n_carts > 0 as has_cart,
    n_orders > 0 as has_order,
    n_carts > 0 and n_orders = 0 as is_abandoned,

    -- hours from first cart to first order (only if the order came after the cart)
    case
        when first_order_time >= first_cart_time
        then round((extract(epoch from first_order_time - first_cart_time) / 3600)::numeric, 2)
    end as hours_cart_to_order,

    -- when the order happened
    trim(to_char(first_order_time, 'Day')) as order_weekday,
    extract(hour from first_order_time)::int as order_hour,
    extract(isodow from first_order_time) in (6, 7) as is_weekend_order,

    -- special cases, left out of some analyses
    first_click_time is null or first_click_time > first_event_time as starts_with_cart_or_order,
    first_cart_time >= '2022-08-27' as cart_in_last_days

from sessions
