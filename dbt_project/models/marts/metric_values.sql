-- Metric mart: daily conversion and revenue metrics by variant
-- Depends on: staging.stg_events

SELECT
    event_date                                               AS date,
    variant,
    COUNT(DISTINCT user_id)                                  AS unique_users,
    COUNT(DISTINCT
        CASE WHEN event_type = 'view'
        THEN user_id END)                                    AS viewers,
    COUNT(DISTINCT
        CASE WHEN event_type = 'add_to_cart'
        THEN user_id END)                                    AS cart_adders,
    COUNT(DISTINCT
        CASE WHEN event_type = 'purchase'
        THEN user_id END)                                    AS purchasers,
    ROUND(
        SUM(CASE WHEN event_type = 'purchase'
            THEN revenue ELSE 0 END), 2)                    AS total_revenue,
    ROUND(
        COUNT(DISTINCT CASE WHEN event_type = 'purchase'
              THEN user_id END) * 100.0 /
        NULLIF(COUNT(DISTINCT
               CASE WHEN event_type = 'view'
               THEN user_id END), 0), 2)                    AS conversion_rate_pct,
    ROUND(
        COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart'
              THEN user_id END) * 100.0 /
        NULLIF(COUNT(DISTINCT
               CASE WHEN event_type = 'view'
               THEN user_id END), 0), 2)                    AS add_to_cart_rate_pct
FROM {{ ref('stg_events') }}
GROUP BY
    event_date,
    variant
ORDER BY
    event_date,
    variant
