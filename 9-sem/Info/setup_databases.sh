#!/bin/bash

# TechMarket Database Setup Script
# Quick deployment and data generation

set -e

echo "========================================"
echo " TechMarket Database Setup"
echo "========================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Docker
echo -e "\n${YELLOW}Step 1: Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo " Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo " Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo -e "${GREEN} Docker and Docker Compose are installed${NC}"

# Step 2: Start databases
echo -e "\n${YELLOW}Step 2: Starting databases...${NC}"
docker-compose up -d

echo -e "${YELLOW}Waiting for databases to be ready (60 seconds)...${NC}"
sleep 60

# Check if all containers are healthy
echo -e "${YELLOW}Checking database health...${NC}"
docker-compose ps

# Step 3: Install Python dependencies
echo -e "\n${YELLOW}Step 3: Installing Python dependencies...${NC}"
if ! command -v python3 &> /dev/null; then
    echo " Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

pip3 install -q -r database/data/requirements.txt
echo -e "${GREEN} Python dependencies installed${NC}"

# Step 4: Generate test data
echo -e "\n${YELLOW}Step 4: Generating test data...${NC}"
python3 database/data/generate_test_data.py

# Step 5: Verify data
echo -e "\n${YELLOW}Step 5: Verifying data...${NC}"

echo ""
echo "=== CATALOG DB ==="
docker-compose exec -T catalog-db mysql -u catalog_user -pcatalog_pass catalog_db -e "SELECT 'Categories' as Table_Name, COUNT(*) as Count FROM categories UNION ALL SELECT 'Products', COUNT(*) FROM products;" 2>/dev/null

echo ""
echo "=== ORDERS DB ==="
docker-compose exec -T orders-db mysql -u orders_user -porders_pass orders_db -e "SELECT 'Regions' as Table_Name, COUNT(*) as Count FROM regions UNION ALL SELECT 'Employees', COUNT(*) FROM employees UNION ALL SELECT 'Customers', COUNT(*) FROM customers UNION ALL SELECT 'Orders', COUNT(*) FROM orders UNION ALL SELECT 'Order Items', COUNT(*) FROM order_items;" 2>/dev/null

echo ""
echo "=== AUTH DB ==="
docker-compose exec -T auth-db mysql -u auth_user -pauth_pass auth_db -e "SELECT 'Users' as Table_Name, COUNT(*) as Count FROM auth_users UNION ALL SELECT 'Roles', COUNT(*) FROM roles UNION ALL SELECT 'Tokens', COUNT(*) FROM auth_tokens;" 2>/dev/null

echo ""
echo "=== PAYMENTS DB ==="
docker-compose exec -T payments-db mysql -u payments_user -ppayments_pass payments_db -e "SELECT 'Payments' as Table_Name, COUNT(*) as Count FROM payments;" 2>/dev/null

echo ""
echo "========================================"
echo -e "${GREEN} Setup completed successfully!${NC}"
echo "========================================"
echo ""
echo " Access Information:"
echo "  - Adminer UI: http://localhost:8080"
echo ""
echo "  - Auth DB:     localhost:3306 (auth_user / auth_pass)"
echo "  - Catalog DB:  localhost:3307 (catalog_user / catalog_pass)"
echo "  - Orders DB:   localhost:3308 (orders_user / orders_pass)"
echo "  - Payments DB: localhost:3309 (payments_user / payments_pass)"
echo "  - DWH DB:      localhost:5432 (dwh_user / dwh_pass)"
echo ""
echo " Useful commands:"
echo "  - Stop:    docker-compose stop"
echo "  - Restart: docker-compose restart"
echo "  - Logs:    docker-compose logs -f"
echo "  - Clean:   docker-compose down -v"
echo ""
