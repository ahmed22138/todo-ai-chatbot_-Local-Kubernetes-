# Backend Helm Chart

Helm chart for deploying the Todo AI Chatbot FastAPI backend on Kubernetes.

## Overview

This chart deploys a FastAPI-based backend application with PostgreSQL database connectivity, JWT authentication, and OpenAI API integration.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Minikube (for local deployment)
- Backend Docker image: `todo-backend:1.0.0`
- Database chart installed first (`todo-database`)

## Installation

### Install the chart

```bash
# Ensure database is running first
helm install todo-backend ./charts/backend
```

### Install with custom values

```bash
helm install todo-backend ./charts/backend -f my-values.yaml
```

### Upgrade the release

```bash
helm upgrade todo-backend ./charts/backend
```

### Uninstall the release

```bash
helm uninstall todo-backend
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of backend replicas | `1` |
| `image.repository` | Backend image repository | `todo-backend` |
| `image.tag` | Backend image tag | `1.0.0` |
| `image.pullPolicy` | Image pull policy | `Never` |
| `backend.port` | Application port | `8000` |
| `backend.environment` | Runtime environment | `development` |
| `backend.allowedOrigins` | CORS allowed origins | `*` |
| `backend.database.host` | Database service hostname | `todo-database-service` |
| `backend.database.port` | Database port | `5432` |
| `backend.database.name` | Database name | `todo_chatbot` |
| `backend.database.username` | Database username | `todouser` |
| `backend.jwtSecret` | JWT signing secret key | `(default key)` |
| `backend.openaiApiKey` | OpenAI API key | `(placeholder)` |
| `service.type` | Kubernetes service type | `NodePort` |
| `service.port` | Service port | `8000` |
| `service.nodePort` | NodePort port | `30800` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `250m` |
| `resources.requests.memory` | Memory request | `256Mi` |
| `livenessProbe.enabled` | Enable liveness probe | `true` |
| `readinessProbe.enabled` | Enable readiness probe | `true` |

## Deployed Resources

- **Deployment**: 1 replica of FastAPI backend with health probes
- **Service**: NodePort service exposing port 8000 on port 30800
- **ConfigMap**: Environment variables (ENVIRONMENT, PORT, DB connection info)
- **Secret**: JWT secret, OpenAI API key, database password

## Health Endpoints

| Endpoint | Purpose | Probe |
|----------|---------|-------|
| `/health` | Application health check | Liveness (30s delay, 10s period) |
| `/health` | Readiness verification | Readiness (10s delay, 5s period) |

## Usage

### Monitor the deployment

```bash
kubectl get pods -l app.kubernetes.io/name=backend -w
kubectl get svc todo-backend-service
kubectl logs -l app.kubernetes.io/name=backend --tail=50
```

### Troubleshooting

```bash
kubectl describe deployment todo-backend
kubectl get events --sort-by='.lastTimestamp'
kubectl port-forward svc/todo-backend-service 5000:8000
```

## Dependencies

This chart requires the `database` chart to be deployed first. The backend connects to PostgreSQL via the `todo-database-service` Kubernetes DNS name.
