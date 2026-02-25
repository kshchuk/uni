-- Check existing indexes and table statistics

-- 1. Check existing indexes
SELECT 
  tablename, 
  indexname, 
  indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
  AND tablename IN ('fact_sales', 'dim_date', 'dim_product', 'dim_region', 'dim_customer', 'dim_employee', 'dim_category')
ORDER BY tablename, indexname;

-- 2. Table row counts
SELECT 
  schemaname,
  tablename,
  n_live_tup AS row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;

-- 3. Index usage statistics
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan AS times_used,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- 4. Table sizes
SELECT 
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
  pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
