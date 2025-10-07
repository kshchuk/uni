# TechMarket - Kubernetes Deployment Guide

## Prerequisites

- Kubernetes cluster (minikube, Docker Desktop with Kubernetes, or cloud provider)
- kubectl configured to access your cluster
- Minimum 4GB RAM available for the cluster

## Quick Start

### 1. Deploy Infrastructure

```bash
# Create namespace and secrets
kubectl apply -f k8s/00-namespace-secrets.yaml

# Create ConfigMaps with SQL initialization scripts
chmod +x k8s/create-configmaps.sh
./k8s/create-configmaps.sh

# Deploy MySQL databases
kubectl apply -f k8s/mysql/

# Deploy PostgreSQL DWH
kubectl apply -f k8s/postgres/
```

### 2. Verify Deployment

```bash
# Check all resources
kubectl get all -n techmarket

# Check pods status
kubectl get pods -n techmarket

# Check services
kubectl get svc -n techmarket

# Check persistent volumes
kubectl get pvc -n techmarket
```

### 3. Access Databases

#### Option A: Port Forwarding

```bash
# Auth DB (MySQL)
kubectl port-forward -n techmarket svc/auth-db 3306:3306

# Catalog DB (MySQL)
kubectl port-forward -n techmarket svc/catalog-db 3307:3306

# Orders DB (MySQL)
kubectl port-forward -n techmarket svc/orders-db 3308:3306

# Payments DB (MySQL)
kubectl port-forward -n techmarket svc/payments-db 3309:3306

# DWH DB (PostgreSQL)
kubectl port-forward -n techmarket svc/dwh-db 5432:5432
```

Then connect using local MySQL/PostgreSQL clients:
```bash
# MySQL example
mysql -h 127.0.0.1 -P 3306 -u auth_user -pauth_pass auth_db

# PostgreSQL example
psql -h 127.0.0.1 -p 5432 -U dwh_user -d dwh_db
# Password: dwh_pass
```

#### Option B: Direct Pod Access

```bash
# Connect to Auth DB
kubectl exec -it auth-db-0 -n techmarket -- mysql -u auth_user -pauth_pass auth_db

# Connect to DWH DB
kubectl exec -it dwh-db-0 -n techmarket -- psql -U dwh_user -d dwh_db
```

### 4. Populate Test Data

After port-forwarding the databases, run the data generator:

```bash
# Install Python dependencies
pip install -r database/data/requirements.txt

# Generate test data
python3 database/data/generate_test_data.py
```

## Resource Configuration

### Storage

All databases use PersistentVolumeClaims with the following sizes:
- Auth DB: 5Gi
- Catalog DB: 5Gi
- Orders DB: 10Gi
- Payments DB: 5Gi
- DWH DB: 5Gi

Default StorageClass: `hostpath` (for Docker Desktop)

To use a different StorageClass, edit the `storageClassName` field in:
- `k8s/mysql/*.yaml`
- `k8s/postgres/*.yaml`

### Resource Limits

MySQL Databases:
- Requests: 512Mi RAM, 250m CPU
- Limits: 1Gi RAM, 500m CPU

Orders DB (larger):
- Requests: 1Gi RAM, 500m CPU
- Limits: 2Gi RAM, 1000m CPU

PostgreSQL DWH:
- Requests: 256Mi RAM, 250m CPU
- Limits: 1Gi RAM, 500m CPU

## Services

All databases are exposed as ClusterIP services:

| Service | Port | Target DB |
|---------|------|-----------|
| auth-db | 3306 | MySQL |
| catalog-db | 3306 | MySQL |
| orders-db | 3306 | MySQL |
| payments-db | 3306 | MySQL |
| dwh-db | 5432 | PostgreSQL |

## Secrets

Database credentials are stored in Kubernetes secrets:

**mysql-secrets:**
- root-password: rootpass
- auth-user/password
- catalog-user/password
- orders-user/password
- payments-user/password

**postgres-secrets:**
- dwh-user: dwh_user
- dwh-password: dwh_pass

To view secrets:
```bash
kubectl get secret mysql-secrets -n techmarket -o yaml
kubectl get secret postgres-secrets -n techmarket -o yaml
```

## Troubleshooting

### Pods stuck in Pending

Check PVC status:
```bash
kubectl get pvc -n techmarket
kubectl describe pvc <pvc-name> -n techmarket
```

Check StorageClass:
```bash
kubectl get storageclass
```

### Pods crash or restart

Check logs:
```bash
kubectl logs -n techmarket <pod-name>
kubectl logs -n techmarket <pod-name> --previous
```

Check pod details:
```bash
kubectl describe pod <pod-name> -n techmarket
```

### Insufficient resources

Reduce resource requests/limits in StatefulSet manifests:
- Edit `k8s/mysql/*.yaml`
- Edit `k8s/postgres/*.yaml`
- Apply changes: `kubectl apply -f <file>`

### Database initialization failed

Check if ConfigMaps are created:
```bash
kubectl get configmap -n techmarket
```

View SQL script content:
```bash
kubectl get configmap auth-db-init-script -n techmarket -o yaml
```

Re-create ConfigMaps:
```bash
./k8s/create-configmaps.sh
```

### Cannot connect to database

Check if pod is running:
```bash
kubectl get pods -n techmarket
```

Check service:
```bash
kubectl get svc -n techmarket
kubectl describe svc auth-db -n techmarket
```

Test connection from within cluster:
```bash
kubectl run -it --rm debug --image=mysql:8.0 --restart=Never -n techmarket -- \
  mysql -h auth-db -u auth_user -pauth_pass auth_db -e "SELECT 1;"
```

## Cleanup

### Remove all resources but keep data
```bash
kubectl delete statefulset --all -n techmarket
kubectl delete service --all -n techmarket
```

### Remove everything including data
```bash
kubectl delete namespace techmarket
```

### Remove specific database
```bash
kubectl delete statefulset auth-db -n techmarket
kubectl delete service auth-db -n techmarket
kubectl delete pvc auth-db-pvc -n techmarket
```

## Scaling (Not Recommended for Databases)

StatefulSets can be scaled, but database replication is not configured:

```bash
# Scale up (creates additional pods but without replication)
kubectl scale statefulset auth-db -n techmarket --replicas=3

# Scale down
kubectl scale statefulset auth-db -n techmarket --replicas=1
```

Note: For production, implement proper database replication before scaling.

## Monitoring

### Check pod health
```bash
# All pods
kubectl get pods -n techmarket -w

# Specific pod with more details
kubectl get pod auth-db-0 -n techmarket -o yaml
```

### Check resource usage
```bash
kubectl top pods -n techmarket
kubectl top nodes
```

### View events
```bash
kubectl get events -n techmarket --sort-by='.lastTimestamp'
```

## Backup and Restore

### Backup

```bash
# MySQL backup
kubectl exec auth-db-0 -n techmarket -- \
  mysqldump -u root -prootpass auth_db > backup_auth.sql

# PostgreSQL backup
kubectl exec dwh-db-0 -n techmarket -- \
  pg_dump -U dwh_user dwh_db > backup_dwh.sql
```

### Restore

```bash
# MySQL restore
cat backup_auth.sql | kubectl exec -i auth-db-0 -n techmarket -- \
  mysql -u root -prootpass auth_db

# PostgreSQL restore
cat backup_dwh.sql | kubectl exec -i dwh-db-0 -n techmarket -- \
  psql -U dwh_user dwh_db
```

## Production Considerations

For production deployment, consider:

1. **High Availability**: Configure MySQL replication and PostgreSQL streaming replication
2. **Persistent Storage**: Use cloud provider storage classes (AWS EBS, GCP PD, Azure Disk)
3. **Resource Limits**: Adjust based on actual workload
4. **Monitoring**: Deploy Prometheus + Grafana for metrics
5. **Backups**: Implement automated backup solutions (Velero, cloud-native tools)
6. **Security**: 
   - Use stronger passwords stored in external secret managers (Vault, AWS Secrets Manager)
   - Enable TLS for database connections
   - Implement network policies
7. **Observability**: Add logging solutions (ELK, Loki)

## Architecture

```
techmarket namespace
├── StatefulSets
│   ├── auth-db (MySQL 8.0)
│   ├── catalog-db (MySQL 8.0)
│   ├── orders-db (MySQL 8.0)
│   ├── payments-db (MySQL 8.0)
│   └── dwh-db (PostgreSQL 15)
├── Services (ClusterIP)
│   ├── auth-db:3306
│   ├── catalog-db:3306
│   ├── orders-db:3306
│   ├── payments-db:3306
│   └── dwh-db:5432
├── PersistentVolumeClaims
│   ├── auth-db-pvc (5Gi)
│   ├── catalog-db-pvc (5Gi)
│   ├── orders-db-pvc (10Gi)
│   ├── payments-db-pvc (5Gi)
│   └── dwh-db-pvc (5Gi)
├── ConfigMaps
│   ├── auth-db-init-script
│   ├── catalog-db-init-script
│   ├── orders-db-init-script
│   ├── payments-db-init-script
│   └── dwh-db-init-script
└── Secrets
    ├── mysql-secrets
    └── postgres-secrets
```
