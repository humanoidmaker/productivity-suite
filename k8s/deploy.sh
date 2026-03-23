#!/bin/bash
set -e

echo "=== Productivity Suite K8s Deployment ==="

echo "[1/6] Creating namespace..."
kubectl apply -f namespace.yaml

echo "[2/6] Applying secrets and config..."
kubectl apply -f secrets.yaml
kubectl apply -f configmap.yaml

echo "[3/6] Deploying infrastructure (PostgreSQL, Redis, MinIO)..."
kubectl apply -f postgres/
kubectl apply -f redis/
kubectl apply -f minio/

echo "Waiting for infra pods..."
kubectl wait --for=condition=ready pod -l app=postgres -n productivity --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n productivity --timeout=60s

echo "[4/6] Deploying backend + Celery..."
kubectl apply -f backend/
kubectl apply -f celery-worker/
kubectl apply -f celery-beat/

echo "Waiting for backend..."
kubectl wait --for=condition=ready pod -l app=backend -n productivity --timeout=120s

echo "[5/6] Deploying frontends..."
kubectl apply -f frontend-app/
kubectl apply -f frontend-admin/

echo "[6/6] Applying ingress..."
kubectl apply -f ingress.yaml

echo ""
echo "=== Deployment Complete ==="
echo "App:   http://app.productivity.local"
echo "Admin: http://admin.productivity.local"
echo "API:   http://api.productivity.local"
