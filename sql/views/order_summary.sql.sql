CREATE OR REPLACE VIEW order_summary AS

WITH payment_agg AS (
    SELECT
        order_id,
        SUM(payment_value) AS total_payment,
        COUNT(*) AS payment_count,
        AVG(payment_value) AS avg_payment
    FROM payments
    GROUP BY order_id
),

items_agg AS (
    SELECT
        order_id,
        COUNT(*) AS total_items,
        SUM(price) AS total_product_value,
        SUM(freight_value) AS total_freight_value
    FROM order_items
    GROUP BY order_id
),

review_agg AS (
    SELECT
        order_id,
        AVG(review_score) AS avg_review_score,
        COUNT(*) AS total_reviews
    FROM reviews
    GROUP BY order_id
)

SELECT
    o.order_id,
    o.customer_id,
    o.order_status,

    -- Dates
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    -- Payment info
    COALESCE(ROUND(p.total_payment::numeric, 2), 0) AS total_payment,
    COALESCE(p.payment_count, 0) AS payment_count,
    COALESCE(ROUND(p.avg_payment::numeric, 2), 0) AS avg_payment,

    -- Items info
    COALESCE(i.total_items, 0) AS total_items,
    COALESCE(ROUND(i.total_product_value::numeric, 2), 0) AS total_product_value,
    COALESCE(ROUND(i.total_freight_value::numeric, 2), 0) AS total_freight_value,

    -- Reviews
    COALESCE(ROUND(r.avg_review_score::numeric, 2), 0) AS avg_review_score,
    COALESCE(r.total_reviews, 0) AS total_reviews,

    -- Derived features (VERY IMPORTANT)
    EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400 AS delivery_time_days,

    EXTRACT(EPOCH FROM (o.order_estimated_delivery_date - o.order_purchase_timestamp)) / 86400 AS estimated_delivery_days,

    EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_estimated_delivery_date)) / 86400 AS delivery_delay_days

FROM orders o

LEFT JOIN payment_agg p
    ON o.order_id = p.order_id

LEFT JOIN items_agg i
    ON o.order_id = i.order_id

LEFT JOIN review_agg r
    ON o.order_id = r.order_id;