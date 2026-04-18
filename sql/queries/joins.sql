-- Orders + customers
SELECT
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    c.customer_id,
    c.customer_city,
    c.customer_state
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
LIMIT 100;

-- Orders + order_items + products
SELECT
    o.order_id,
    o.order_purchase_timestamp,
    oi.order_item_id,
    oi.product_id,
    p.product_category_name,
    oi.price,
    oi.freight_value
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
LIMIT 100;

-- Orders + payments
SELECT
    o.order_id,
    o.order_status,
    pay.payment_type,
    pay.payment_installments,
    pay.payment_value
FROM orders o
JOIN payments pay
    ON o.order_id = pay.order_id
LIMIT 100;

-- Orders + reviews
SELECT
    o.order_id,
    o.order_status,
    r.review_score,
    r.review_comment_message
FROM orders o
JOIN reviews r
    ON o.order_id = r.order_id
LIMIT 100;

Full business join
SELECT
    o.order_id,
    o.order_purchase_timestamp,
    c.customer_city,
    c.customer_state,
    oi.product_id,
    p.product_category_name,
    pay.payment_type,
    pay.payment_value,
    r.review_score
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN payments pay
    ON o.order_id = pay.order_id
LEFT JOIN reviews r
    ON o.order_id = r.order_id
LIMIT 100;

