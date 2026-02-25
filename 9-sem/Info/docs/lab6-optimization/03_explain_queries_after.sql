-- Lab 6: EXPLAIN ANALYZE для KPI запитів ПІСЛЯ оптимізації
-- Дата: 2024-11-28
-- Використання індексів та матеріалізованих представлень

-- =====================================================
-- Query 1: Revenue by Month (using materialized view)
-- =====================================================
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING) 
SELECT
  year,
  month,
  SUM(total_revenue) AS revenue,
  SUM(total_discount) AS discount,
  SUM(total_margin) AS margin
FROM mv_monthly_sales
WHERE year = 2024
GROUP BY year, month
ORDER BY year, month;

-- =====================================================
-- Query 1 Alternative: Using optimized indexes on base tables
-- =====================================================
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING) 
SELECT
  d.year,
  d.month,
  to_char(d.date, 'Mon') AS month_name,
  SUM(f.revenue) AS revenue,
  SUM(f.discount_amount) AS discount,
  SUM(f.margin) AS margin
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
LEFT JOIN dim_region r ON f.region_key = r.region_key
WHERE d.date >= '2024-01-01' AND d.date <= '2024-12-31'
GROUP BY d.year, d.month, to_char(d.date, 'Mon')
ORDER BY d.year, d.month;

-- =====================================================
-- Query 2: Orders by Region (using materialized view)
-- =====================================================
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING)
SELECT
  region_name,
  orders_count,
  total_revenue AS revenue
FROM mv_regional_performance
ORDER BY orders_count DESC;

-- =====================================================
-- Query 2 Alternative: Using optimized indexes
-- =====================================================
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING)
SELECT
  r.name AS region_name,
  COUNT(DISTINCT f.order_id) AS orders_count,
  SUM(f.revenue) AS revenue
FROM fact_sales f
JOIN dim_region r ON f.region_key = r.region_key
WHERE f.date_key >= 20240101 AND f.date_key <= 20241231
GROUP BY r.name
ORDER BY orders_count DESC;

-- =====================================================
-- Query 3: Average Order Value (using materialized view)
-- =====================================================
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING)
SELECT
  SUM(total_revenue) / NULLIF(SUM(orders_count), 0) AS avg_order_value
FROM mv_monthly_sales
WHERE year = 2024;

-- =====================================================
-- Query 4: Margin Percentage (using materialized view)
-- =====================================================
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING)
SELECT
  (SUM(total_margin) / NULLIF(SUM(total_revenue), 0))::numeric(12,4) AS margin_pct
FROM mv_monthly_sales
WHERE year = 2024;

-- =====================================================
-- Query 5: Top Products by Revenue (using materialized view)
-- =====================================================
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING)
SELECT
  product_name,
  total_revenue AS revenue,
  total_quantity AS qty,
  total_margin AS margin
FROM mv_product_performance
ORDER BY total_revenue DESC
LIMIT 10;

-- =====================================================
-- Query 5 Alternative: Using optimized indexes
-- =====================================================
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING)
SELECT
  p.name AS product_name,
  SUM(f.revenue) AS revenue,
  SUM(f.quantity) AS qty,
  SUM(f.margin) AS margin
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
LEFT JOIN dim_region r ON f.region_key = r.region_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date >= '2024-01-01' AND d.date <= '2024-12-31'
GROUP BY p.name
ORDER BY revenue DESC
LIMIT 10;
