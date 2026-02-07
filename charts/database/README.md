# Database Helm Chart

Helm chart for deploying PostgreSQL database for the Todo AI Chatbot on Kubernetes.

## Overview

This chart deploys a PostgreSQL 16 (Alpine) database as a StatefulSet with persistent storage, used as the primary data store for the Todo AI Chatbot application.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Minikube (for local deployment)
- Storage class `standard` available (default in Minikube)

## Installation

### Install the chart

```bash
helm install todo-database ./charts/database
```

### Wait for database to be ready

```bash
kubectl wait --for=condition=ready pod/todo-database-0 --timeout=120s
```

### Install with custom values

```bash
helm install todo-database ./charts/database -f my-values.yaml
```

### Upgrade the release

```bash
helm upgrade todo-database ./charts/database
```

### Uninstall the release

```bash
helm uninstall todo-database
# Also remove PVC to delete data
kubectl delete pvc data-todo-database-0
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | PostgreSQL image | `postgres` |
| `image.tag` | PostgreSQL version | `16-alpine` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `postgresql.database` | Database name | `todo_chatbot` |
| `postgresql.username` | Database username | `todouser` |
| `postgresql.password` | Database password | `todopass123` |
| `postgresql.port` | Database port | `5432` |
| `persistence.enabled` | Enable persistent storage | `true` |
| `persistence.size` | PVC storage size | `5Gi` |
| `persistence.storageClass` | Storage class | `standard` |
| `resources.limits.cpu` | CPU limit | `300m` |
| `resources.limits.memory` | Memory limit | `256Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `5432` |

## Deployed Resources

- **StatefulSet**: 1 replica PostgreSQL with persistent volume
- **Service**: ClusterIP service on port 5432 (internal only)
- **Headless Service**: For StatefulSet DNS resolution
- **Secret**: Database credentials (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD)
- **PersistentVolumeClaim**: 5Gi storage for database data

## Health Probes

| Probe | Command | Config |
|-------|---------|--------|
| Liveness | `pg_isready -U todouser -d todo_chatbot` | 30s delay, 10s period, 6 failures |
| Readiness | `pg_isready -U todouser -d todo_chatbot` | 5s delay, 5s period, 3 failures |

## Usage

### Connect to database

```bash
# From within the cluster (exec into backend pod)
kubectl exec -it <backend-pod> -- python -c "import asyncio; print('DB connected')"

# Direct access for debugging
kubectl port-forward svc/todo-database-service 5432:5432
psql -h localhost -U todouser -d todo_chatbot
```

### Check database status

```bash
kubectl get pods todo-database-0
kubectl logs todo-database-0 --tail=20
kubectl exec todo-database-0 -- pg_isready -U todouser -d todo_chatbot
```

### Backup and restore

```bash
# Backup
kubectl exec todo-database-0 -- pg_dump -U todouser todo_chatbot > backup.sql

# Restore
kubectl exec -i todo-database-0 -- psql -U todouser todo_chatbot < backup.sql
```

## Notes

- Data persists across pod restarts via PersistentVolumeClaim
- The headless service is required for StatefulSet DNS resolution
- Password is stored in a Kubernetes Secret (change in production)
- Internal-only service (ClusterIP) - not exposed outside the cluster
