-- Which customer states generate the most revenue?
SELECT
    c.customer_state,
    ROUND(SUM(p.payment_value)::numeric, 2) AS revenue
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
JOIN payments p
    ON o.order_id = p.order_id
GROUP BY c.customer_state
ORDER BY revenue DESC;

-- Which product categories generate the highest revenue?
SELECT
    pr.product_category_name,
    ROUND(SUM(oi.price + oi.freight_value)::numeric, 2) AS revenue
FROM order_items oi
JOIN products pr
    ON oi.product_id = pr.product_id
GROUP BY pr.product_category_name
ORDER BY revenue DESC
LIMIT 15;

--  Does delivery delay affect review score?
WITH order_delivery AS (
    SELECT
        o.order_id,
        r.review_score,
        EXTRACT(DAY FROM (o.order_delivered_customer_date - o.order_estimated_delivery_date)) AS delivery_delay_days
    FROM orders o
    JOIN reviews r
        ON o.order_id = r.order_id
    WHERE o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
)
SELECT
    CASE
        WHEN delivery_delay_days <= 0 THEN 'On time or early'
        WHEN delivery_delay_days BETWEEN 1 AND 3 THEN '1 to 3 days late'
        WHEN delivery_delay_days BETWEEN 4 AND 7 THEN '4 to 7 days late'
        ELSE 'More than 7 days late'
    END AS delay_group,
    COUNT(*) AS orders_count,
    ROUND(AVG(review_score)::numeric, 2) AS avg_review_score
FROM order_delivery
GROUP BY delay_group
ORDER BY avg_review_score DESC;

--  Which payment type is most used?
SELECT
    payment_type,
    COUNT(*) AS times_used,
    ROUND(AVG(payment_value)::numeric, 2) AS avg_payment_value
FROM payments
GROUP BY payment_type
ORDER BY times_used DESC;

--  Which sellers sell the most revenue?
SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,
    ROUND(SUM(oi.price + oi.freight_value)::numeric, 2) AS revenue
FROM order_items oi
JOIN sellers s
    ON oi.seller_id = s.seller_id
GROUP BY s.seller_id, s.seller_city, s.seller_state
ORDER BY revenue DESC
LIMIT 10;

--  Which months had the highest revenue?
SELECT
    TO_CHAR(DATE_TRUNC('month', o.order_purchase_timestamp), 'YYYY-MM') AS month,
    ROUND(SUM(p.payment_value)::numeric, 2) AS revenue
FROM orders o
JOIN payments p
    ON o.order_id = p.order_id
GROUP BY DATE_TRUNC('month', o.order_purchase_timestamp)
ORDER BY revenue DESC;

--  What is the average order value by state?
SELECT
    c.customer_state,
    ROUND(AVG(p.payment_value)::numeric, 2) AS avg_order_value
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
JOIN payments p
    ON o.order_id = p.order_id
GROUP BY c.customer_state
ORDER BY avg_order_value DESC;

--  Which categories have the best average review score?
SELECT
    pr.product_category_name,
    ROUND(AVG(r.review_score)::numeric, 2) AS avg_review_score,
    COUNT(*) AS review_count
FROM order_items oi
JOIN products pr
    ON oi.product_id = pr.product_id
JOIN orders o
    ON oi.order_id = o.order_id
JOIN reviews r
    ON o.order_id = r.order_id
GROUP BY pr.product_category_name
HAVING COUNT(*) >= 50
ORDER BY avg_review_score DESC;