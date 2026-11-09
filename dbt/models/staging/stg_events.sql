-- one row per event, with clear names and Berlin time

with source as (
    select * from {{ source('otto', 'raw_events') }}
),

renamed as (
    select
        session as session_id,
        aid as product_id,
        type as event_type,
        to_timestamp(ts / 1000.0) at time zone 'Europe/Berlin' as event_time
    from source
)

select
    session_id,
    product_id,
    event_type,
    event_time,
    event_time::date as event_date
from renamed
