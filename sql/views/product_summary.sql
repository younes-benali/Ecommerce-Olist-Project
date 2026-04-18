-- Create product_summary view
CREATE OR REPLACE VIEW product_summary AS
WITH product_sales AS (
    
    SELECT
        oi.product_id,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        SUM(oi.price) AS total_revenue,
        AVG(oi.price) AS avg_price,
        SUM(oi.freight_value) AS total_freight,
        AVG(oi.freight_value) AS avg_freight,
        COUNT(oi.order_item_id) AS total_items_sold
    FROM order_items oi
    GROUP BY oi.product_id
),
product_reviews AS (
    SELECT
        oi.product_id,
        AVG(r.review_score) AS avg_review_score,
        COUNT(r.review_id) AS total_reviews
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN reviews r ON o.order_id = r.order_id
    GROUP BY oi.product_id
)
SELECT
    p.product_id,
    p.product_category_name,
    p.product_name_length,
    p.product_description_length,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    COALESCE(ps.total_orders, 0) AS total_orders,
    COALESCE(ps.total_revenue, 0) AS total_revenue,
    COALESCE(ps.avg_price, 0) AS avg_price,
    COALESCE(ps.total_freight, 0) AS total_freight,
    COALESCE(ps.avg_freight, 0) AS avg_freight,
    COALESCE(ps.total_items_sold, 0) AS total_items_sold,
    COALESCE(pr.avg_review_score, 0) AS avg_review_score,
    COALESCE(pr.total_reviews, 0) AS total_reviews
FROM products p
LEFT JOIN product_sales ps ON p.product_id = ps.product_id
LEFT JOIN product_reviews pr ON p.product_id = pr.product_id;