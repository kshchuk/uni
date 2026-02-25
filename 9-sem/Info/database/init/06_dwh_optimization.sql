-- =====================================================
-- Lab 6: DWH Optimization Script
-- Date: 2024-11-28
-- Purpose: Create indexes and materialized views for query optimization
-- =====================================================

-- =====================================================
-- PART 1: COMPOSITE INDEXES FOR fact_sales
-- =====================================================

-- Index for date + product queries (Revenue by Month, Top Products)
CREATE INDEX IF NOT EXISTS idx_fact_sales_date_product 
  ON fact_sales(date_key, product_key);

-- Index for date + region queries (Orders by Region)
CREATE INDEX IF NOT EXISTS idx_fact_sales_date_region 
  ON fact_sales(date_key, region_key);

-- Index for date + customer queries
CREATE INDEX IF NOT EXISTS idx_fact_sales_date_customer 
  ON fact_sales(date_key, customer_key);

-- Index for date + employee queries
CREATE INDEX IF NOT EXISTS idx_fact_sales_date_employee 
  ON fact_sales(date_key, employee_key);

-- Index for order_id (used in COUNT DISTINCT)
CREATE INDEX IF NOT EXISTS idx_fact_sales_order_id 
  ON fact_sales(order_id);

-- BRIN index for sequential date_key data (space-efficient)
CREATE INDEX IF NOT EXISTS idx_fact_sales_date_brin 
  ON fact_sales USING BRIN(date_key);

-- Covering index for product revenue queries
CREATE INDEX IF NOT EXISTS idx_fact_sales_product_revenue 
  ON fact_sales(product_key) INCLUDE (revenue, quantity, margin, discount_amount);

-- Covering index for region revenue queries
CREATE INDEX IF NOT EXISTS idx_fact_sales_region_revenue 
  ON fact_sales(region_key) INCLUDE (revenue, margin, order_id);

-- =====================================================
-- PART 2: INDEXES FOR DIMENSION TABLES
-- =====================================================

-- Index for date range queries on dim_date
CREATE INDEX IF NOT EXISTS idx_dim_date_date_range 
  ON dim_date(date);

-- Index for year/month queries
CREATE INDEX IF NOT EXISTS idx_dim_date_year_month 
  ON dim_date(year, month);

-- Index for product name searches
CREATE INDEX IF NOT EXISTS idx_dim_product_name 
  ON dim_product(name);

-- Index for region name searches
CREATE INDEX IF NOT EXISTS idx_dim_region_name 
  ON dim_region(name);

-- =====================================================
-- PART 3: MATERIALIZED VIEW - Monthly Sales Summary
-- =====================================================

DROP MATERIALIZED VIEW IF EXISTS mv_monthly_sales CASCADE;

CREATE MATERIALIZED VIEW mv_monthly_sales AS
SELECT
  d.year,
  d.month,
  d.quarter,
  r.region_key,
  r.name AS region_name,
  r.code AS region_code,
  COUNT(DISTINCT f.order_id) AS orders_count,
  COUNT(f.sales_key) AS items_count,
  SUM(f.revenue) AS total_revenue,
  SUM(f.discount_amount) AS total_discount,
  SUM(f.margin) AS total_margin,
  SUM(f.quantity) AS total_quantity,
  AVG(f.revenue) AS avg_item_revenue,
  MIN(f.revenue) AS min_revenue,
  MAX(f.revenue) AS max_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
LEFT JOIN dim_region r ON f.region_key = r.region_key
GROUP BY d.year, d.month, d.quarter, r.region_key, r.name, r.code;

-- Indexes for materialized view
CREATE INDEX idx_mv_monthly_sales_year_month 
  ON mv_monthly_sales(year, month);

CREATE INDEX idx_mv_monthly_sales_region 
  ON mv_monthly_sales(region_key);

CREATE INDEX idx_mv_monthly_sales_revenue 
  ON mv_monthly_sales(total_revenue DESC);

-- =====================================================
-- PART 4: MATERIALIZED VIEW - Product Performance
-- =====================================================

DROP MATERIALIZED VIEW IF EXISTS mv_product_performance CASCADE;

CREATE MATERIALIZED VIEW mv_product_performance AS
SELECT
  p.product_key,
  p.product_id,
  p.name AS product_name,
  p.sku,
  c.category_key,
  c.name AS category_name,
  COUNT(DISTINCT f.order_id) AS orders_count,
  COUNT(f.sales_key) AS items_sold,
  SUM(f.quantity) AS total_quantity,
  SUM(f.revenue) AS total_revenue,
  SUM(f.discount_amount) AS total_discount,
  SUM(f.margin) AS total_margin,
  SUM(f.cost) AS total_cost,
  AVG(f.revenue) AS avg_revenue_per_sale,
  AVG(f.margin) AS avg_margin_per_sale,
  MAX(d.date) AS last_sale_date,
  MIN(d.date) AS first_sale_date
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
LEFT JOIN dim_category c ON p.category_key = c.category_key
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY p.product_key, p.product_id, p.name, p.sku, c.category_key, c.name;

-- Indexes for product performance view
CREATE INDEX idx_mv_product_performance_revenue 
  ON mv_product_performance(total_revenue DESC);

CREATE INDEX idx_mv_product_performance_margin 
  ON mv_product_performance(total_margin DESC);

CREATE INDEX idx_mv_product_performance_category 
  ON mv_product_performance(category_name);

CREATE INDEX idx_mv_product_performance_sku 
  ON mv_product_performance(sku);

-- =====================================================
-- PART 5: MATERIALIZED VIEW - Regional Performance
-- =====================================================

DROP MATERIALIZED VIEW IF EXISTS mv_regional_performance CASCADE;

CREATE MATERIALIZED VIEW mv_regional_performance AS
SELECT
  r.region_key,
  r.region_id,
  r.name AS region_name,
  r.code AS region_code,
  COUNT(DISTINCT f.order_id) AS orders_count,
  COUNT(DISTINCT f.customer_key) AS unique_customers,
  COUNT(DISTINCT f.employee_key) AS active_employees,
  COUNT(DISTINCT f.product_key) AS unique_products,
  COUNT(f.sales_key) AS total_items,
  SUM(f.revenue) AS total_revenue,
  SUM(f.discount_amount) AS total_discount,
  SUM(f.margin) AS total_margin,
  SUM(f.cost) AS total_cost,
  AVG(f.revenue) AS avg_item_revenue,
  SUM(f.revenue) / NULLIF(COUNT(DISTINCT f.order_id), 0) AS avg_order_value,
  SUM(f.margin) / NULLIF(SUM(f.revenue), 0) AS margin_percentage
FROM fact_sales f
JOIN dim_region r ON f.region_key = r.region_key
GROUP BY r.region_key, r.region_id, r.name, r.code;

-- Indexes for regional performance view
CREATE INDEX idx_mv_regional_performance_revenue 
  ON mv_regional_performance(total_revenue DESC);

CREATE INDEX idx_mv_regional_performance_orders 
  ON mv_regional_performance(orders_count DESC);

CREATE INDEX idx_mv_regional_performance_code 
  ON mv_regional_performance(region_code);

-- =====================================================
-- PART 6: MATERIALIZED VIEW - Customer Performance
-- =====================================================

DROP MATERIALIZED VIEW IF EXISTS mv_customer_performance CASCADE;

CREATE MATERIALIZED VIEW mv_customer_performance AS
SELECT
  c.customer_key,
  c.customer_id,
  c.first_name,
  c.last_name,
  c.email,
  r.region_key,
  r.name AS region_name,
  COUNT(DISTINCT f.order_id) AS orders_count,
  COUNT(f.sales_key) AS items_purchased,
  SUM(f.quantity) AS total_quantity,
  SUM(f.revenue) AS total_revenue,
  SUM(f.margin) AS total_margin,
  AVG(f.revenue) AS avg_item_revenue,
  SUM(f.revenue) / NULLIF(COUNT(DISTINCT f.order_id), 0) AS avg_order_value,
  MAX(d.date) AS last_purchase_date,
  MIN(d.date) AS first_purchase_date
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
LEFT JOIN dim_region r ON c.region_key = r.region_key
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY c.customer_key, c.customer_id, c.first_name, c.last_name, c.email, r.region_key, r.name;

-- Indexes for customer performance view
CREATE INDEX idx_mv_customer_performance_revenue 
  ON mv_customer_performance(total_revenue DESC);

CREATE INDEX idx_mv_customer_performance_orders 
  ON mv_customer_performance(orders_count DESC);

CREATE INDEX idx_mv_customer_performance_email 
  ON mv_customer_performance(email);

-- =====================================================
-- PART 7: VACUUM AND ANALYZE
-- =====================================================

-- Update table statistics
VACUUM ANALYZE fact_sales;
VACUUM ANALYZE dim_date;
VACUUM ANALYZE dim_product;
VACUUM ANALYZE dim_region;
VACUUM ANALYZE dim_customer;
VACUUM ANALYZE dim_employee;
VACUUM ANALYZE dim_category;

-- Analyze materialized views
ANALYZE mv_monthly_sales;
ANALYZE mv_product_performance;
ANALYZE mv_regional_performance;
ANALYZE mv_customer_performance;

-- =====================================================
-- PART 8: VIEW STATISTICS
-- =====================================================

-- Display optimization results
SELECT 'Optimization completed successfully!' AS status;

SELECT 
  'Total indexes created' AS metric,
  COUNT(*) AS value
FROM pg_indexes 
WHERE schemaname = 'public' 
  AND indexname LIKE 'idx_%';

SELECT 
  'Materialized views created' AS metric,
  COUNT(*) AS value
FROM pg_matviews 
WHERE schemaname = 'public';

-- Display materialized view sizes
SELECT 
  matviewname,
  pg_size_pretty(pg_total_relation_size('public.' || matviewname)) AS size
FROM pg_matviews
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size('public.' || matviewname) DESC;
