--  Customer lifetime value summary 
WITH customer_orders AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS total_orders,
        MIN(o.order_purchase_timestamp) AS first_order_date,
        MAX(o.order_purchase_timestamp) AS last_order_date
    FROM orders o
    GROUP BY o.customer_id
),
customer_revenue AS (
    SELECT
        o.customer_id,
        SUM(p.payment_value) AS total_spent
    FROM orders o
    JOIN payments p
        ON o.order_id = p.order_id
    GROUP BY o.customer_id
)
SELECT
    c.customer_id,
    co.total_orders,
    co.first_order_date,
    co.last_order_date,
    ROUND(cr.total_spent::numeric, 2) AS total_spent
FROM customers c
LEFT JOIN customer_orders co
    ON c.customer_id = co.customer_id
LEFT JOIN customer_revenue cr
    ON c.customer_id = cr.customer_id
ORDER BY total_spent DESC NULLS LAST;

--Monthly revenue with moving average
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
        SUM(p.payment_value) AS revenue
    FROM orders o
    JOIN payments p
        ON o.order_id = p.order_id
    GROUP BY DATE_TRUNC('month', o.order_purchase_timestamp)
)
SELECT
    month,
    ROUND(revenue::numeric, 2) AS revenue,
    ROUND(AVG(revenue) OVER (
        ORDER BY month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    )::numeric, 2) AS moving_avg_3_months
FROM monthly_revenue
ORDER BY month;


-- Cohort style first purchase month vs later purchases
WITH first_purchase AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_purchase_timestamp)) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
customer_orders AS (
    SELECT
        o.customer_id,
        DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month
    FROM orders o
)
SELECT

    fp.cohort_month,
    co.order_month,
    COUNT(DISTINCT co.customer_id) AS customers_count
FROM first_purchase fp
JOIN customer_orders co
    ON fp.customer_id = co.customer_id
GROUP BY fp.cohort_month, co.order_month
ORDER BY fp.cohort_month, co.order_month;