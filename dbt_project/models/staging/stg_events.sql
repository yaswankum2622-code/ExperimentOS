-- Staging model: clean and standardise raw events
-- Source: events table loaded by data/loader.py

SELECT
    event_id,
    user_id,
    event_type,
    timestamp,
    invoice_id,
    product_id,
    COALESCE(revenue, 0)       AS revenue,
    country,
    variant,
    DATE(timestamp)            AS event_date,
    strftime('%W', timestamp)  AS event_week,
    strftime('%Y', timestamp)  AS event_year
FROM events
WHERE
    event_type IN ('view', 'add_to_cart', 'purchase')
    AND user_id IS NOT NULL
    AND timestamp IS NOT NULL
