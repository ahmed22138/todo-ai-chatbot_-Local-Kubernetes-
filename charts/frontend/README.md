# T073: Frontend Helm Chart

Helm chart for deploying the Todo AI Chatbot frontend application on Kubernetes.

## Overview

This chart deploys a React-based frontend application served by Nginx, configured for Single Page Application (SPA) routing.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Minikube (for local deployment)
- Frontend Docker image: `todo-frontend:1.0.0`

## Installation

### Install the chart

```bash
helm install todo-frontend ./charts/frontend
```

### Install with custom values

```bash
helm install todo-frontend ./charts/frontend -f my-values.yaml
```

### Upgrade the release

```bash
helm upgrade todo-frontend ./charts/frontend
```

### Uninstall the release

```bash
helm uninstall todo-frontend
```

## Configuration

The following table lists the configurable parameters of the frontend chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of frontend replicas | `2` |
| `image.repository` | Frontend image repository | `todo-frontend` |
| `image.tag` | Frontend image tag | `1.0.0` |
| `image.pullPolicy` | Image pull policy | `Never` |
| `service.type` | Kubernetes service type | `NodePort` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `80` |
| `service.nodePort` | NodePort (if service.type is NodePort) | `30080` |
| `resources.limits.cpu` | CPU limit | `200m` |
| `resources.limits.memory` | Memory limit | `128Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `64Mi` |
| `probes.liveness.enabled` | Enable liveness probe | `true` |
| `probes.readiness.enabled` | Enable readiness probe | `true` |
| `config.backendUrl` | Backend API URL | `http://todo-backend-service:5000` |

## Usage

### Access the application

After installation, get the application URL:

```bash
# For NodePort service
minikube service todo-frontend-service --url

# Or direct access
echo "http://$(minikube ip):30080"
```

### Monitor the deployment

```bash
# Watch pods
kubectl get pods -l app.kubernetes.io/name=frontend -w

# Check service
kubectl get svc todo-frontend-service

# View logs
kubectl logs -l app.kubernetes.io/name=frontend --tail=50
```

### Troubleshooting

```bash
# Describe deployment
kubectl describe deployment todo-frontend-deployment

# Check pod events
kubectl get events --sort-by='.lastTimestamp'

# Port forward for debugging
kubectl port-forward svc/todo-frontend-service 8080:80
```

## Architecture

The frontend chart deploys:
- **Deployment**: 2 replicas of the frontend application
- **Service**: NodePort service exposing port 80 on port 30080
- **ConfigMap**: Environment variables for backend connection
- **Health Probes**: Liveness and readiness checks on `/`

## Notes

- The image pull policy is set to `Never` for local Minikube deployments
- Nginx is configured for SPA routing (all routes serve `index.html`)
- The frontend communicates with the backend service internally via Kubernetes DNS
