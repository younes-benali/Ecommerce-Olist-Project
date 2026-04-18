CREATE OR REPLACE VIEW sales_summary AS
WITH order_revenue AS (
    SELECT
        o.order_id,
        o.order_purchase_timestamp,
        o.order_status,
        o.customer_id,
        SUM(p.payment_value) AS payment_revenue
    FROM orders o
    JOIN payments p
        ON o.order_id = p.order_id
    GROUP BY
        o.order_id,
        o.order_purchase_timestamp,
        o.order_status,
        o.customer_id
),
order_items_revenue AS (
    SELECT
        oi.order_id,
        SUM(oi.price) AS product_revenue,
        SUM(oi.freight_value) AS freight_revenue,
        COUNT(*) AS total_items
    FROM order_items oi
    GROUP BY oi.order_id
)
SELECT
    DATE_TRUNC('month', orv.order_purchase_timestamp) AS month,
    COUNT(DISTINCT orv.order_id) AS total_orders,
    COUNT(DISTINCT orv.customer_id) AS total_customers,
    SUM(orv.payment_revenue) AS total_payment_revenue,
    SUM(oir.product_revenue) AS total_product_revenue,
    SUM(oir.freight_revenue) AS total_freight_revenue,
    AVG(orv.payment_revenue) AS avg_order_payment,
    SUM(oir.total_items) AS total_items_sold
FROM order_revenue orv
LEFT JOIN order_items_revenue oir
    ON orv.order_id = oir.order_id
GROUP BY DATE_TRUNC('month', orv.order_purchase_timestamp)
ORDER BY month;