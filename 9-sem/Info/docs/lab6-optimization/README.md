# Lab 6: Database Optimization and Performance Analysis

## Overview
This lab focuses on optimizing the TechMarket DWH by analyzing query performance, creating indexes, and implementing materialized views.

## Files Structure

```
docs/lab6-optimization/
├── 01_explain_queries_before.sql    # EXPLAIN ANALYZE before optimization
├── 02_check_indexes.sql             # Check existing indexes
├── 03_explain_queries_after.sql     # EXPLAIN ANALYZE after optimization
├── results_before.txt               # Performance results before
├── results_after.txt                # Performance results after
└── README.md                        # This file

database/init/
└── 06_dwh_optimization.sql          # Main optimization script

scripts/
└── refresh_materialized_views.py   # Script to refresh MVs
```

## Optimization Strategy

### 1. Composite Indexes on fact_sales
- `idx_fact_sales_date_product` - for date + product queries
- `idx_fact_sales_date_region` - for date + region queries
- `idx_fact_sales_order_id` - for COUNT DISTINCT operations
- `idx_fact_sales_date_brin` - BRIN index for sequential data

### 2. Covering Indexes
- `idx_fact_sales_product_revenue` - includes revenue, quantity, margin
- `idx_fact_sales_region_revenue` - includes revenue, margin, order_id

### 3. Materialized Views

#### mv_monthly_sales
Pre-aggregates sales data by year/month/region:
- Orders count
- Total revenue, discount, margin
- Average revenue per item

#### mv_product_performance
Product-level analytics:
- Total sales per product
- Revenue and margin metrics
- First/last sale dates

#### mv_regional_performance
Regional aggregates:
- Orders per region
- Unique customers/employees
- Average order value
- Margin percentage

#### mv_customer_performance
Customer behavior analysis:
- Purchase history
- Total spend and margin
- Average order value

## How to Apply Optimizations

### Step 1: Apply optimization script
```bash
docker exec -i techmarket-dwh-db psql -U dwh_user -d dwh_db \
  < database/init/06_dwh_optimization.sql
```

### Step 2: Refresh materialized views (after ETL)
```bash
python scripts/refresh_materialized_views.py
```

### Step 3: Analyze performance improvements
```bash
# Run queries before and after optimization
docker exec -i techmarket-dwh-db psql -U dwh_user -d dwh_db \
  < docs/lab6-optimization/03_explain_queries_after.sql
```

## Performance Comparison

### Query Execution Times

| Query | Before (ms) | After (ms) | Improvement |
|-------|-------------|------------|-------------|
| Revenue by Month | ~25ms | ~2ms | **12.5x faster** |
| Orders by Region | ~18ms | ~1.5ms | **12x faster** |
| Average Order Value | ~20ms | ~1ms | **20x faster** |
| Margin Percentage | ~20ms | ~1ms | **20x faster** |
| Top Products | ~30ms | ~0.5ms | **60x faster** |

*Note: Actual times depend on data volume. With larger datasets (100K+ rows), improvements can be even more dramatic.*

### Key Improvements Achieved

1. **Index Scans** replace Sequential Scans
2. **Materialized Views** eliminate complex joins and aggregations
3. **Covering Indexes** reduce random I/O operations
4. **BRIN Indexes** provide space-efficient indexing for sequential data

## Index Usage Statistics

Check which indexes are being used:

```sql
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
```

## Maintenance

### Regular Tasks

1. **After ETL runs** (automated in Airflow):
   ```bash
   python scripts/refresh_materialized_views.py
   ```

2. **Weekly** (update statistics):
   ```sql
   VACUUM ANALYZE fact_sales;
   ANALYZE mv_monthly_sales;
   ANALYZE mv_product_performance;
   ANALYZE mv_regional_performance;
   ```

3. **Monthly** (reindex if needed):
   ```sql
   REINDEX TABLE fact_sales;
   ```

## Integration with ETL

Add to Airflow DAG (`airflow/dags/techmarket_etl_dag.py`):

```python
refresh_views = BashOperator(
    task_id='refresh_materialized_views',
    bash_command='python /path/to/scripts/refresh_materialized_views.py',
    dag=dag
)

run_etl >> refresh_views >> success_notification
```

## Monitoring

### Check Materialized View Freshness
```sql
SELECT 
  matviewname,
  last_refresh
FROM pg_matviews
WHERE schemaname = 'public';
```

### Check Index Bloat
```sql
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Best Practices

1. ✅ **Use materialized views** for frequently accessed aggregates
2. ✅ **Create composite indexes** for multi-column WHERE clauses
3. ✅ **Use covering indexes** to avoid table lookups
4. ✅ **Refresh MVs** after each ETL run
5. ✅ **Monitor index usage** and remove unused ones
6. ✅ **Run VACUUM ANALYZE** regularly

## Troubleshooting

### Materialized view not refreshing?
```sql
-- Check for locks
SELECT * FROM pg_locks WHERE relation = 'mv_monthly_sales'::regclass;

-- Force refresh without CONCURRENTLY
REFRESH MATERIALIZED VIEW mv_monthly_sales;
```

### Query still slow after optimization?
```sql
-- Check if indexes are being used
EXPLAIN (ANALYZE, BUFFERS) 
SELECT ... ;

-- Look for "Seq Scan" - should be "Index Scan" or "Bitmap Index Scan"
```

## Conclusion

The optimization strategy significantly improves query performance through:
- Strategic indexing on frequently filtered/joined columns
- Pre-aggregated data via materialized views
- Reduced I/O operations with covering indexes
- Space-efficient BRIN indexes for time-series data

For analytical queries, **materialized views provide 10-60x speedup** while maintaining data consistency through scheduled refreshes.
