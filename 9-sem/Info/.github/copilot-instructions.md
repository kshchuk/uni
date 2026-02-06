# TechMarket Database Infrastructure - AI Agent Instructions

## Project Overview
TechMarket is a **Database-per-Service microservices architecture** for an e-commerce platform with separated OLTP (MySQL) and OLAP (PostgreSQL) databases. The system demonstrates enterprise data architecture patterns including ETL simulation, schema-first design using DBML, and multi-environment deployment (Docker Compose + Kubernetes).

## Critical Architecture Principles

### Database Isolation (Database-per-Service Pattern)
- **NO cross-database foreign keys** - Each service owns its data completely
- Services reference entities across databases using IDs only (documented in DBML comments)
- Example: `auth_users.customer_id` references `orders_db.customers.id` but has NO FK constraint
- UUIDs stored as `CHAR(36)` in MySQL (native UUID type unsupported)

### Dual Schema Management System
1. **Source of Truth: DBML files** in `docs/db/*.dbml`
   - Manually edited, version controlled
   - Use `CHAR(36)` for UUIDs, explicit `varchar(N)` lengths, `decimal(P,S)` precision
2. **Generated SQL schemas** in `database/init/*.sql`
   - Generated via: `dbml2sql <file>.dbml --mysql -o database/init/<N>_schema.sql`
   - Auto-mounted in Docker containers via `/docker-entrypoint-initdb.d/`
   - **Never edit SQL directly** - regenerate from DBML instead

### Port Mapping Convention
```
Auth DB:     localhost:3306  (MySQL)
Catalog DB:  localhost:3307  (MySQL)
Orders DB:   localhost:3308  (MySQL)
Payments DB: localhost:3309  (MySQL)
DWH DB:      localhost:5432  (PostgreSQL)
Adminer:     localhost:8080  (Web UI)
```

## Essential Workflows

### Schema Changes (Critical Order)
```bash
# 1. Edit DBML source
vim docs/db/auth_mysql.dbml

# 2. Regenerate SQL
cd docs/db
dbml2sql auth_mysql.dbml --mysql -o ../../database/init/01_auth_schema.sql

# 3. Recreate databases (data will be lost!)
docker-compose down -v
docker-compose up -d

# 4. Wait for healthy status (check healthchecks)
sleep 15 && docker-compose ps

# 5. Regenerate test data
python3 database/data/generate_test_data.py
```

### Test Data Generation
The `generate_test_data.py` script:
- Connects to **running databases** (must be healthy first)
- Populates OLTP databases with realistic Faker data
- **Simulates ETL**: reads from MySQL OLTP → transforms → loads to PostgreSQL DWH
- Uses dictionary cursor mode for MySQL (`cursor = conn.cursor(dictionary=True)`)
- Critical: Column names in queries must match actual schema (e.g., `discount` not `discount_percent`)

### Quick Reset Workflow
```bash
make clean   # Stop + remove volumes
make start   # Recreate databases
# Wait 15s for initialization
python3 database/data/generate_test_data.py
```

## Project-Specific Conventions

### DBML Type Mapping Rules
- **UUID**: Always `char(36)` (not `uuid` - MySQL doesn't support it)
- **Strings**: Explicit lengths required: `varchar(255)`, `varchar(100)`
- **Decimals**: Explicit precision: `decimal(10,2)` for money
- **Foreign Keys**: Use `ref: > table.column` syntax in DBML
- **Comments**: Document cross-DB references: `[note: 'Ref: Orders DB (customers.id), без FK']`

### Python Data Generator Patterns
- **UUID generation**: `str(uuid.uuid4())` (not `uuid.uuid4()` directly)
- **Date ranges**: Uses Faker + manual ranges for realistic distribution
- **Hierarchical data**: Categories populate parent→child order via `ORDER BY parent_category_id IS NULL DESC`
- **ETL simulation**: Builds dimension tables first, then fact table with surrogate key mappings
- **Error handling**: MySQL/PostgreSQL connection errors printed with stack traces

### Docker Compose Structure
- All databases use **named volumes** (e.g., `techmarket-auth-db-data`)
- Healthchecks required before data generation (10s interval, 5 retries)
- SQL scripts auto-run on first container start via `/docker-entrypoint-initdb.d/`
- Shared network: `techmarket-network` (bridge driver)

### Kubernetes Deployment Specifics
- Uses **StatefulSets** (not Deployments) for stable pod identities
- **ConfigMaps** for SQL init scripts (created via `k8s/create-configmaps.sh`)
- **Secrets** for credentials (in `00-namespace-secrets.yaml`)
- **Storage class**: `hostpath` (for Docker Desktop K8s) - adjust for cloud providers
- **Resource limits**: MySQL (512Mi-2Gi), PostgreSQL (256Mi-1Gi) - critical for local K8s

## Common Pitfalls & Solutions

### ❌ "Unknown column 'parent_id'" Error
**Cause**: Query uses wrong column name  
**Fix**: Check actual schema - likely `parent_category_id` or similar  
**Prevention**: Always verify column names via `DESCRIBE table` before writing queries

### ❌ "Duplicate entry" on Data Generation
**Cause**: Databases contain old data  
**Fix**: Run `docker-compose down -v` to remove volumes  
**Prevention**: Always use `-v` flag when resetting databases

### ❌ Kubernetes Pod Stuck in Pending
**Cause**: PVC can't bind (wrong storage class)  
**Fix**: Change `storageClassName: standard` → `hostpath` (Docker Desktop) or appropriate class  
**Check**: `kubectl describe pvc -n techmarket`

### ❌ "Password authentication failed" (PostgreSQL)
**Cause**: Username/password mismatch  
**Fix**: 
- Username: `dwh_user` (not `dwh_db`)
- Maintenance DB: `postgres` (not `dwh_db`)
- Password: `dwh_pass`

## Key Files Reference

### Schema Flow
```
docs/db/*.dbml              → Source of truth (edit here)
    ↓ (dbml2sql)
database/init/*.sql         → Generated schemas (auto-loaded)
    ↓ (docker-entrypoint-initdb.d)
Running MySQL/PostgreSQL    → Active databases
```

### Documentation Hierarchy
- `README.md`: Quick start + architecture overview
- `DATABASE_README.md`: Docker Compose deep dive (~300 lines)
- `KUBERNETES_README.md`: K8s deployment guide (~400 lines)
- `LAB_REPORT.md`: Step-by-step execution report with screenshots
- `SCREENSHOT_INSTRUCTIONS.md`: Guide for creating ~35-40 screenshots

### Critical Python Modules
- `database/data/generate_test_data.py`: 700+ lines, all data generation logic
  - Functions: `populate_auth_db()`, `populate_catalog_db()`, `populate_orders_db()`, `populate_payments_db()`, `populate_dwh_db()`
  - Always runs in order: Catalog → Orders → Auth → Payments → DWH

## Testing & Verification

### Verify Database Content
```bash
make verify  # Shows row counts for all tables
```

### Manual SQL Access
```bash
# MySQL
docker-compose exec auth-db mysql -u auth_user -pauth_pass auth_db

# PostgreSQL
docker-compose exec dwh-db psql -U dwh_user -d dwh_db
```

### Check Kubernetes Status
```bash
kubectl get pods -n techmarket          # Should show 5/5 Running
kubectl get pvc -n techmarket           # Should show all Bound
kubectl logs auth-db-0 -n techmarket    # Check init logs
```

## Makefile Commands (Developer Shortcuts)
- `make setup`: Full automated setup (Docker + data)
- `make clean`: Nuclear option - removes all volumes
- `make verify`: Quick sanity check on data counts
- `make backup`: Dumps all DBs to `backups/` directory
- `make k8s-deploy`: Full K8s deployment sequence

## Language & Localization
- **Code comments**: Ukrainian (`uk_UA`)
- **Documentation**: Ukrainian
- **Test data**: Mixed Ukrainian/English (Faker locales: `['uk_UA', 'en_US']`)
- **Error messages**: English (from libraries)

## Python Development Standards

### Code Quality Requirements
- **Python Version**: Always assume Python 3.12
- **Style Guide**: Follow PEP 8 strictly for clean, production-grade code
- **Design Patterns**: Use well-known Python design patterns and OOP approaches
- **String Formatting**: Prefer f-strings over `.format()` or `%` formatting

### Documentation & Type Safety
- **Docstrings**: Use Google-style docstrings for all functions, classes, and modules
- **Type Hints**: MUST provide type hints for function parameters and return values
- **Type Annotations**: Use modern type hints (`list[str]`, `dict[str, int]`) not legacy (`List`, `Dict`)

### Code Organization Patterns
- **Properties**: Use `@property` decorator for getter/setter methods instead of direct attribute access
- **Dataclasses**: Use `@dataclass` for data storage classes instead of regular classes with `__init__`
- **Generators**: Use generators for large datasets to optimize memory usage
- **Logging**: Replace `print()` statements with proper `logging` module for production code

### Error Handling
- **External Dependencies**: Implement robust error handling when calling databases, APIs, or external services
- **Try-Except Blocks**: Catch specific exceptions, not bare `except:`
- **Context Managers**: Use `with` statements for resource management (file handles, DB connections)

### Example Pattern (from `generate_test_data.py`)
```python
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Configuration for database connection.
    
    Attributes:
        host: Database host address
        port: Database port number
        user: Database username
        password: Database password
        database: Database name
    """
    host: str
    port: int
    user: str
    password: str
    database: str

def generate_uuid() -> str:
    """Generate UUID as string for MySQL CHAR(36) compatibility.
    
    Returns:
        UUID string in format: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
    """
    return str(uuid.uuid4())
```

## When Making Changes
1. **Schema changes**: Always edit DBML first, never SQL directly
2. **Data generation**: Verify column names match schema before running
3. **Docker changes**: Test with `make clean && make setup` for clean slate
4. **K8s changes**: Verify resource limits suitable for target cluster
5. **Documentation**: Update relevant README if changing deployment process
6. **Python code**: Follow all Python Development Standards above
