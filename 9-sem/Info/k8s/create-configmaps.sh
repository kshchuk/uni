#!/bin/bash
# Script to create ConfigMaps from SQL init scripts for Kubernetes

NAMESPACE="techmarket"
INIT_DIR="./database/init"

echo " Creating ConfigMaps for database initialization scripts..."

# Check if namespace exists, create if not
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo "📦 Creating namespace: $NAMESPACE"
    kubectl create namespace $NAMESPACE
fi

# Create ConfigMaps for each database
echo " Creating ConfigMap for Auth DB..."
kubectl create configmap auth-db-init-script \
    --from-file=01_schema.sql=$INIT_DIR/01_auth_schema.sql \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

echo " Creating ConfigMap for Catalog DB..."
kubectl create configmap catalog-db-init-script \
    --from-file=02_schema.sql=$INIT_DIR/02_catalog_schema.sql \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

echo " Creating ConfigMap for Orders DB..."
kubectl create configmap orders-db-init-script \
    --from-file=03_schema.sql=$INIT_DIR/03_orders_schema.sql \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

echo " Creating ConfigMap for Payments DB..."
kubectl create configmap payments-db-init-script \
    --from-file=04_schema.sql=$INIT_DIR/04_payments_schema.sql \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

echo " Creating ConfigMap for DWH DB..."
kubectl create configmap dwh-db-init-script \
    --from-file=05_schema.sql=$INIT_DIR/05_dwh_schema.sql \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

echo " All ConfigMaps created successfully!"
