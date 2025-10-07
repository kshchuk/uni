.PHONY: help setup start stop restart logs clean verify backup adminer k8s-deploy k8s-clean

# Default target
help:
	@echo "TechMarket Database Management"
	@echo ""
	@echo "Docker Compose Commands:"
	@echo "  make setup      - Full setup: start databases and generate test data"
	@echo "  make start      - Start all databases"
	@echo "  make stop       - Stop all databases"
	@echo "  make restart    - Restart all databases"
	@echo "  make logs       - Show logs from all containers"
	@echo "  make clean      - Stop and remove all containers and volumes"
	@echo "  make verify     - Verify database content"
	@echo "  make backup     - Backup all databases"
	@echo "  make adminer    - Open Adminer in browser"
	@echo ""
	@echo "Kubernetes Commands:"
	@echo "  make k8s-deploy - Deploy to Kubernetes"
	@echo "  make k8s-clean  - Clean Kubernetes deployment"
	@echo ""

# Full setup with data generation
setup:
	@echo " Starting full setup..."
	@./setup_databases.sh

# Start databases
start:
	@echo "  Starting databases..."
	@docker-compose up -d
	@echo " Databases started"
	@docker-compose ps

# Stop databases
stop:
	@echo "  Stopping databases..."
	@docker-compose stop
	@echo " Databases stopped"

# Restart databases
restart:
	@echo "🔄 Restarting databases..."
	@docker-compose restart
	@echo " Databases restarted"

# Show logs
logs:
	@docker-compose logs -f

# Clean everything
clean:
	@echo "🧹 Cleaning up..."
	@docker-compose down -v
	@echo " Cleanup complete"

# Verify database content
verify:
	@echo "=== CATALOG DB ==="
	@docker-compose exec -T catalog-db mysql -u catalog_user -pcatalog_pass catalog_db \
		-e "SELECT 'Categories' as Table_Name, COUNT(*) as Count FROM categories UNION ALL SELECT 'Products', COUNT(*) FROM products;" 2>/dev/null
	@echo ""
	@echo "=== ORDERS DB ==="
	@docker-compose exec -T orders-db mysql -u orders_user -porders_pass orders_db \
		-e "SELECT 'Regions' as Table_Name, COUNT(*) as Count FROM regions UNION ALL SELECT 'Employees', COUNT(*) FROM employees UNION ALL SELECT 'Customers', COUNT(*) FROM customers UNION ALL SELECT 'Orders', COUNT(*) FROM orders UNION ALL SELECT 'Order Items', COUNT(*) FROM order_items;" 2>/dev/null
	@echo ""
	@echo "=== AUTH DB ==="
	@docker-compose exec -T auth-db mysql -u auth_user -pauth_pass auth_db \
		-e "SELECT 'Users' as Table_Name, COUNT(*) as Count FROM auth_users UNION ALL SELECT 'Roles', COUNT(*) FROM roles UNION ALL SELECT 'Tokens', COUNT(*) FROM auth_tokens;" 2>/dev/null
	@echo ""
	@echo "=== PAYMENTS DB ==="
	@docker-compose exec -T payments-db mysql -u payments_user -ppayments_pass payments_db \
		-e "SELECT 'Payments' as Table_Name, COUNT(*) as Count FROM payments;" 2>/dev/null

# Backup databases
backup:
	@echo " Creating backups..."
	@mkdir -p backups
	@docker-compose exec -T auth-db mysqldump -u root -prootpass auth_db > backups/auth_db_$$(date +%Y%m%d_%H%M%S).sql
	@docker-compose exec -T catalog-db mysqldump -u root -prootpass catalog_db > backups/catalog_db_$$(date +%Y%m%d_%H%M%S).sql
	@docker-compose exec -T orders-db mysqldump -u root -prootpass orders_db > backups/orders_db_$$(date +%Y%m%d_%H%M%S).sql
	@docker-compose exec -T payments-db mysqldump -u root -prootpass payments_db > backups/payments_db_$$(date +%Y%m%d_%H%M%S).sql
	@docker-compose exec -T dwh-db pg_dump -U dwh_user dwh_db > backups/dwh_db_$$(date +%Y%m%d_%H%M%S).sql
	@echo " Backups created in ./backups/"
	@ls -lh backups/ | tail -5

# Open Adminer in browser
adminer:
	@echo " Opening Adminer..."
	@xdg-open http://localhost:8080 2>/dev/null || open http://localhost:8080 2>/dev/null || echo "Please open http://localhost:8080 in your browser"

# Kubernetes deployment
k8s-deploy:
	@echo "  Deploying to Kubernetes..."
	@kubectl apply -f k8s/00-namespace-secrets.yaml
	@./k8s/create-configmaps.sh
	@kubectl apply -f k8s/mysql/
	@kubectl apply -f k8s/postgres/
	@echo " Kubernetes deployment complete"
	@echo ""
	@kubectl get pods -n techmarket

# Clean Kubernetes deployment
k8s-clean:
	@echo "🧹 Cleaning Kubernetes deployment..."
	@kubectl delete namespace techmarket
	@echo " Kubernetes cleanup complete"
