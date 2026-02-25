#!/bin/bash
# Test and verify Lab 6 optimizations

set -e

echo "=============================================="
echo "Lab 6: Testing Database Optimizations"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database connection
DB_CONTAINER="techmarket-dwh-db"
DB_USER="dwh_user"
DB_NAME="dwh_db"

# Step 1: Check if database is running
echo -e "${BLUE}Step 1: Checking database status...${NC}"
if docker ps | grep -q "$DB_CONTAINER"; then
    echo -e "${GREEN}✓ Database container is running${NC}"
else
    echo -e "${YELLOW}⚠ Database container is not running. Starting...${NC}"
    docker compose up -d dwh-db
    sleep 5
fi
echo ""

# Step 2: Check data exists
echo -e "${BLUE}Step 2: Checking data in DWH...${NC}"
ROW_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM fact_sales;")
echo "fact_sales rows: $ROW_COUNT"
if [ "$ROW_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Data exists in DWH${NC}"
else
    echo -e "${YELLOW}⚠ No data found. Run ETL first: python etl/run_etl.py --mode full${NC}"
fi
echo ""

# Step 3: Check existing indexes
echo -e "${BLUE}Step 3: Checking existing indexes...${NC}"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT COUNT(*) AS index_count 
FROM pg_indexes 
WHERE schemaname = 'public' AND indexname LIKE 'idx_%';"
echo ""

# Step 4: Apply optimizations
echo -e "${BLUE}Step 4: Applying optimizations...${NC}"
docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < database/init/06_dwh_optimization.sql
echo -e "${GREEN}✓ Optimizations applied${NC}"
echo ""

# Step 5: Check created indexes
echo -e "${BLUE}Step 5: Verifying indexes...${NC}"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT 
  tablename, 
  COUNT(*) AS index_count
FROM pg_indexes 
WHERE schemaname = 'public' 
  AND tablename IN ('fact_sales', 'dim_date', 'dim_product', 'dim_region')
GROUP BY tablename
ORDER BY tablename;"
echo ""

# Step 6: Check materialized views
echo -e "${BLUE}Step 6: Verifying materialized views...${NC}"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT 
  matviewname,
  pg_size_pretty(pg_total_relation_size('public.' || matviewname)) AS size
FROM pg_matviews
WHERE schemaname = 'public'
ORDER BY matviewname;"
echo ""

# Step 7: Run performance test
echo -e "${BLUE}Step 7: Running performance test...${NC}"
echo "Testing Query: Revenue by Month (using MV)"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
EXPLAIN (ANALYZE, TIMING)
SELECT year, month, SUM(total_revenue) AS revenue
FROM mv_monthly_sales
WHERE year = 2024
GROUP BY year, month
ORDER BY year, month;" | grep "Execution Time"
echo ""

# Step 8: Test refresh script
echo -e "${BLUE}Step 8: Testing materialized view refresh...${NC}"
if [ -f "scripts/refresh_materialized_views.py" ]; then
    python scripts/refresh_materialized_views.py
    echo -e "${GREEN}✓ Refresh script works${NC}"
else
    echo -e "${YELLOW}⚠ Refresh script not found${NC}"
fi
echo ""

# Step 9: Index usage statistics
echo -e "${BLUE}Step 9: Index usage statistics...${NC}"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT 
  tablename,
  indexname,
  idx_scan AS times_used
FROM pg_stat_user_indexes
WHERE schemaname = 'public' 
  AND indexname LIKE 'idx_%'
  AND idx_scan > 0
ORDER BY idx_scan DESC
LIMIT 10;"
echo ""

# Final summary
echo -e "${GREEN}=============================================="
echo "✓ All optimization tests completed!"
echo "=============================================="
echo -e "${NC}"
echo "Next steps:"
echo "1. Review docs/lab6-optimization/README.md"
echo "2. Compare performance: docs/lab6-optimization/results_before.txt vs results_after.txt"
echo "3. Add refresh task to Airflow DAG"
echo ""
