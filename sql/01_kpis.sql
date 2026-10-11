-- sql/01_kpis.sql
-- Core business KPIs, built on the tables loaded by load_db.py
-- Run these in SSMS, connected to the olist_analytics database.

-- ============================================================
-- 1. TOTAL REVENUE AND ORDER VOLUME
-- ============================================================
-- Revenue = price + freight_value, summed across all order items.
-- We only count 'delivered' orders - undelivered orders (canceled,
-- unavailable) shouldn't count as real revenue.

SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.price + oi.freight_value) AS total_revenue,
    SUM(oi.price + oi.freight_value) / COUNT(DISTINCT o.order_id) AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered';

-- ============================================================
-- 2. MONTHLY REVENUE TREND
-- ============================================================
-- FORMAT() extracts year-month from the purchase date so we can
-- group by month. This feeds the trend line chart in Power BI.

SELECT
    FORMAT(o.order_purchase_timestamp, 'yyyy-MM') AS order_month,
    SUM(oi.price + oi.freight_value) AS monthly_revenue,
    COUNT(DISTINCT o.order_id) AS monthly_orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY FORMAT(o.order_purchase_timestamp, 'yyyy-MM')
ORDER BY order_month;

-- ============================================================
-- 3. REVENUE BY STATE (regional performance)
-- ============================================================

SELECT
    c.customer_state,
    SUM(oi.price + oi.freight_value) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY revenue DESC;

-- ============================================================
-- 4. TOP PRODUCT CATEGORIES BY REVENUE
-- ============================================================
-- LEFT JOIN on category_translation because a few products have
-- no category (we labeled them 'unknown' in clean.py) - LEFT JOIN
-- keeps them instead of silently dropping those rows.

SELECT
    COALESCE(ct.product_category_name_english, p.product_category_name) AS category,
    SUM(oi.price + oi.freight_value) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY COALESCE(ct.product_category_name_english, p.product_category_name)
ORDER BY revenue DESC;
-- COALESCE(a, b) returns 'a' unless it's NULL, then returns 'b'.
-- Here: use the English category name if the translation exists,
-- otherwise fall back to the original Portuguese name.

-- ============================================================
-- 5. TOP 5 PRODUCT CATEGORIES PER STATE (window function)
-- ============================================================
-- This is the "top N per group" pattern from Level 1 theory.

WITH category_revenue AS (
    SELECT
        c.customer_state,
        COALESCE(ct.product_category_name_english, p.product_category_name) AS category,
        SUM(oi.price + oi.freight_value) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state, COALESCE(ct.product_category_name_english, p.product_category_name)
),
ranked AS (
    SELECT *,
        RANK() OVER (PARTITION BY customer_state ORDER BY revenue DESC) AS rnk
    FROM category_revenue
)
SELECT customer_state, category, revenue
FROM ranked
WHERE rnk <= 5
ORDER BY customer_state, rnk;

-- ============================================================
-- 6. AVERAGE DELIVERY TIME (operations KPI)
-- ============================================================
-- DATEDIFF(day, start, end) counts days between two dates.
-- Only delivered orders have a real delivery date.

SELECT
    AVG(DATEDIFF(day, order_purchase_timestamp, order_delivered_customer_date)) AS avg_delivery_days
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL;

-- ============================================================
-- 7. PAYMENT TYPE BREAKDOWN
-- ============================================================

SELECT
    payment_type,
    COUNT(*) AS num_payments,
    SUM(payment_value) AS total_value,
    AVG(payment_value) AS avg_payment
FROM payments
GROUP BY payment_type
ORDER BY total_value DESC;