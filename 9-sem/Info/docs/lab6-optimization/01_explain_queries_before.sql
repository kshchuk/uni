-- Lab 6: EXPLAIN ANALYZE для KPI запитів ДО оптимізації
-- Дата: 2024-11-28

-- =====================================================
-- Query 1: Revenue by Month
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
-- Query 2: Orders by Region
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
-- Query 3: Average Order Value
-- =====================================================
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING)
SELECT
  SUM(f.revenue) / NULLIF(COUNT(DISTINCT f.order_id), 0) AS avg_order_value
FROM fact_sales f
LEFT JOIN dim_region r ON f.region_key = r.region_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date >= '2024-01-01' AND d.date <= '2024-12-31';

-- =====================================================
-- Query 4: Margin Percentage
-- =====================================================
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, TIMING)
SELECT
  (SUM(f.margin) / NULLIF(SUM(f.revenue), 0))::numeric(12,4) AS margin_pct
FROM fact_sales f
LEFT JOIN dim_region r ON f.region_key = r.region_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date >= '2024-01-01' AND d.date <= '2024-12-31';

-- =====================================================
-- Query 5: Top Products by Revenue
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
