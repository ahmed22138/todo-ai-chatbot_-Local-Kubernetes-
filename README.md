# Phase 4: Kubernetes Deployment - Todo AI Chatbot

Complete Kubernetes deployment of the Todo AI Chatbot application using Helm charts on Minikube.

## Quick Start

### Prerequisites
- Docker Desktop running
- Minikube installed and running
- kubectl configured
- Helm 3+ installed

### Deploy the Application

1. **Start Minikube** (if not already running):
```bash
minikube start --cpus=2 --memory=3072
```

2. **Load Docker images to Minikube**:
```bash
minikube image load todo-backend:1.0.0
minikube image load todo-frontend:1.0.0
```

3. **Deploy Database**:
```bash
helm install todo-database charts/database
```

4. **Deploy Backend**:
```bash
helm install todo-backend charts/backend
```

5. **Deploy Frontend**:
```bash
helm install todo-frontend charts/frontend
```

6. **Access the Application**:
```bash
minikube service todo-frontend-service --url
```

### Verify Deployment

Check all components are running:
```bash
kubectl get pods
# All pods should show STATUS: Running

kubectl get svc
# Services should be created

# Test backend health
kubectl run curl-test --image=curlimages/curl:latest --rm -i --restart=Never -- \
  curl -s http://todo-backend-service:8000/health
# Should return: {"status":"healthy","api":"operational","database":"connected"}
```

## Architecture

**3-Tier Application Stack:**
- **Frontend**: React TypeScript + Nginx (2 replicas)
- **Backend**: Python FastAPI (2 replicas)
- **Database**: PostgreSQL 16 (1 replica with persistent storage)

## Components

### Frontend
- **Image**: todo-frontend:1.0.0
- **Service**: NodePort on port 30080
- **Access**: Via `minikube service` command

### Backend
- **Image**: todo-backend:1.0.0
- **Service**: ClusterIP on port 8000
- **Health**: `/health` endpoint
- **API Docs**: `/docs` endpoint

### Database
- **Image**: postgres:16-alpine
- **Service**: ClusterIP on port 5432
- **Storage**: 5Gi persistent volume
- **Database**: todo_chatbot

## Configuration

### Update Backend Environment (if needed)
```bash
# Edit backend values
helm upgrade todo-backend charts/backend \
  --set backend.openaiApiKey="your-api-key-here"
```

### Update Frontend Backend URL (if needed)
```bash
# Edit frontend values
helm upgrade todo-frontend charts/frontend \
  --set config.backendUrl="http://todo-backend-service:8000"
```

## Troubleshooting

### Pods not starting
```bash
# Check pod status
kubectl get pods

# Check pod logs
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>
```

### Storage provisioner issues
```bash
# Restart storage provisioner
minikube addons disable storage-provisioner
minikube addons enable storage-provisioner
```

### Backend database connection issues
```bash
# Check database pod
kubectl get pods -l app.kubernetes.io/name=database

# Check backend logs
kubectl logs -l app.kubernetes.io/name=backend --tail=50
```

## Cleanup

Remove all deployments:
```bash
helm uninstall todo-frontend
helm uninstall todo-backend
helm uninstall todo-database
kubectl delete pvc data-todo-database-0
```

## Documentation

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment documentation including:
- Detailed architecture diagrams
- Resource allocation
- Troubleshooting guide
- Security considerations
- Next steps for production

## Project Structure

```
Phase_4/
├── backend/              # Python FastAPI application
│   ├── src/             # Source code
│   ├── Dockerfile       # Backend container image
│   └── requirements.txt # Python dependencies
├── frontend/            # React TypeScript application
│   ├── src/            # Source code
│   ├── Dockerfile      # Multi-stage frontend build
│   └── nginx.conf      # Nginx configuration
├── charts/             # Helm charts
│   ├── frontend/       # Frontend Helm chart
│   ├── backend/        # Backend Helm chart
│   └── database/       # PostgreSQL Helm chart
├── DEPLOYMENT.md       # Complete deployment documentation
└── README.md          # This file
```

## Status

✅ **Deployment Complete**
- All components deployed successfully
- Health checks passing
- Full stack integration verified
- Documentation complete

## Support

For issues or questions:
1. Check [DEPLOYMENT.md](./DEPLOYMENT.md) troubleshooting section
2. Review pod logs: `kubectl logs <pod-name>`
3. Check service status: `kubectl get svc`
4. Verify resource allocation: `kubectl top pods`

---

**Last Updated**: 2026-01-07
**Status**: Production Ready (with security updates needed for production use)
