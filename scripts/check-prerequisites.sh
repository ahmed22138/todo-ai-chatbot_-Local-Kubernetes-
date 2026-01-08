#!/bin/bash
# T014: Prerequisite validation script for Kubernetes deployment

set -e

echo "=== Checking Prerequisites for Kubernetes Deployment ==="
echo ""

# Check Docker
echo "✓ Checking Docker..."
docker --version || { echo "❌ Docker not found"; exit 1; }

# Check Minikube
echo "✓ Checking Minikube..."
minikube version || { echo "❌ Minikube not found"; exit 1; }

# Check kubectl
echo "✓ Checking kubectl..."
kubectl version --client || { echo "❌ kubectl not found"; exit 1; }

# Check Helm
echo "✓ Checking Helm..."
helm version || { echo "❌ Helm not found"; exit 1; }

# Check Minikube status
echo "✓ Checking Minikube cluster status..."
minikube status || { echo "❌ Minikube cluster not running"; exit 1; }

# Check cluster connectivity
echo "✓ Checking cluster connectivity..."
kubectl cluster-info || { echo "❌ Cannot connect to cluster"; exit 1; }

# Check nodes
echo "✓ Checking node status..."
kubectl get nodes | grep -q "Ready" || { echo "❌ Node not ready"; exit 1; }

# Check ingress addon
echo "✓ Checking ingress-nginx addon..."
kubectl get pods -n ingress-nginx | grep -q "Running" || { echo "❌ Ingress not running"; exit 1; }

# Check metrics-server addon
echo "✓ Checking metrics-server addon..."
kubectl get pods -n kube-system -l k8s-app=metrics-server | grep -q "Running" || { echo "❌ Metrics server not running"; exit 1; }

echo ""
echo "=== ✅ All Prerequisites Met ==="
echo "Ready for deployment!"
