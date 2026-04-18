CREATE OR REPLACE VIEW customer_summary AS
WITH customer_orders AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS total_orders,
        MIN(o.order_purchase_timestamp) AS first_order_date,
        MAX(o.order_purchase_timestamp) AS last_order_date,
        SUM(p.payment_value) AS total_spent,
        AVG(p.payment_value) AS avg_order_value
    FROM orders o
    JOIN payments p
        ON o.order_id = p.order_id
    GROUP BY o.customer_id
),
customer_location AS (
    SELECT DISTINCT
        customer_id,
        customer_city,
        customer_state
    FROM customers
)
SELECT
    c.customer_id,
    c.customer_city,
    c.customer_state,
    COALESCE(co.total_orders, 0) AS total_orders,
    COALESCE(ROUND(co.total_spent::numeric, 2), 0) AS total_spent,
    COALESCE(ROUND(co.avg_order_value::numeric, 2), 0) AS avg_order_value,
    co.first_order_date,
    co.last_order_date
FROM customer_location c
LEFT JOIN customer_orders co
    ON c.customer_id = co.customer_id;