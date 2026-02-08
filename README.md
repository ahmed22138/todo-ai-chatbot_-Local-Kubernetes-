# Phase 4 - Todo AI Chatbot - Kubernetes Deployment

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                  Minikube Cluster                     │
│                                                      │
│  ┌────────────┐   ┌────────────┐   ┌─────────────┐  │
│  │  Frontend   │──▶│  Backend   │──▶│  Database    │  │
│  │  (Nginx)    │   │ (FastAPI)  │   │ (PostgreSQL) │  │
│  │  Port: 80   │   │ Port: 8000 │   │ Port: 5432   │  │
│  │  2 replicas │   │ 1 replica  │   │ 1 replica    │  │
│  └────────────┘   └────────────┘   └─────────────┘  │
│        │                                             │
│   NodePort:30080                                     │
└──────────────────────────────────────────────────────┘
        │
        ▼ (port-forward)
  localhost:3000 ──▶ Browser
```

| Service | Internal Port | NodePort | Type |
|---------|--------------|----------|------|
| todo-frontend-service | 80 | 30080 | NodePort |
| todo-backend-service | 8000 | 30800 | NodePort |
| todo-database-service | 5432 | - | ClusterIP |

---

## Prerequisites

- Docker Desktop (running)
- Minikube installed
- kubectl installed
- Helm 3+ installed

---

## Fresh Deployment (Step by Step)

### Step 1: Start Minikube

```powershell
minikube start --cpus=2 --memory=3072 --driver=docker
```

### Step 2: Enable Addons

```powershell
minikube addons enable ingress
```

```powershell
minikube addons enable metrics-server
```

### Step 3: Build Docker Images

```powershell
cd E:\hackathon-ii\Phase_4
```

```powershell
docker build -t todo-frontend:2.0.3 ./frontend
```

```powershell
docker build -t todo-backend:1.0.0 ./backend
```

### Step 4: Load Images into Minikube

```powershell
minikube image load todo-frontend:2.0.3
```

```powershell
minikube image load todo-backend:1.0.0
```

### Step 5: Deploy Database

```powershell
helm install todo-database charts/database
```

```powershell
kubectl wait --for=condition=ready pod/todo-database-0 --timeout=180s
```


### Step 6: Deploy Backend

```powershell
helm install todo-backend charts/backend -f charts/backend/values-local.yaml
```

```powershell
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=backend --timeout=180s
```

### Step 7: Deploy Frontend

```powershell
helm install todo-frontend charts/frontend
```

```powershell
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=frontend --timeout=180s
```

### Step 8: Verify Deployment

```powershell
kubectl get pods
```

Expected:
```
NAME                                        READY   STATUS
todo-backend-xxxxxxxxx-xxxxx                1/1     Running
todo-database-0                             1/1     Running
todo-frontend-deployment-xxxxxxxxx-xxxxx    1/1     Running
todo-frontend-deployment-xxxxxxxxx-xxxxx    1/1     Running
```

### Step 9: Access App (2 separate PowerShell windows)

**Window 1 - Frontend:**
```powershell
kubectl port-forward svc/todo-frontend-service 3000:80
```

**Window 2 - Backend:**
```powershell
kubectl port-forward svc/todo-backend-service 5000:8000
```

### Step 10: Open Browser

```
http://localhost:3000
```

Signup karo, login karo, chat karo!

---

## PC Restart ke Baad

```powershell
minikube start
```

```powershell
kubectl get pods
```

Agar pods Running dikhayein:
```powershell
kubectl port-forward svc/todo-frontend-service 3000:80
```
```powershell
kubectl port-forward svc/todo-backend-service 5000:8000
```

Agar pods NOT Running:
```powershell
helm install todo-database charts/database
```
```powershell
kubectl wait --for=condition=ready pod/todo-database-0 --timeout=180s
```
```powershell
helm install todo-backend charts/backend
```
```powershell
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=backend --timeout=180s
```
```powershell
helm install todo-frontend charts/frontend
```
```powershell
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=frontend --timeout=180s
```

---

## Cleanup (Sab Band Karna Ho)

```powershell
helm uninstall todo-frontend
```

```powershell
helm uninstall todo-backend
```

```powershell
helm uninstall todo-database
```

```powershell
kubectl delete pvc --all
```

```powershell
minikube stop
```

Pura cluster delete karna ho:
```powershell
minikube delete
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Check pods | `kubectl get pods` |
| Check services | `kubectl get services` |
| Backend logs | `kubectl logs -l app.kubernetes.io/name=backend --tail=50` |
| Frontend logs | `kubectl logs -l app.kubernetes.io/name=frontend --tail=50` |
| Database logs | `kubectl logs todo-database-0 --tail=50` |
| Restart backend | `kubectl rollout restart deployment todo-backend` |
| Restart frontend | `kubectl rollout restart deployment todo-frontend-deployment` |
| Describe pod | `kubectl describe pod <pod-name>` |
| Exec into pod | `kubectl exec -it <pod-name> -- /bin/sh` |
| Minikube status | `minikube status` |
| Minikube IP | `minikube ip` |
| Helm releases | `helm list` |
| Smoke tests | `bash scripts/validate-deployment.sh` |

---

## Troubleshooting

### Pods stuck in Pending
```powershell
kubectl describe pod <pod-name>
```

### ErrImageNeverPull
Image Minikube mein load nahi hui:
```powershell
minikube image load todo-frontend:2.0.3
minikube image load todo-backend:1.0.0
kubectl rollout restart deployment <deployment-name>
```

### Backend CrashLoopBackOff
```powershell
kubectl logs -l app.kubernetes.io/name=backend --tail=50
```

### Cannot connect to localhost:3000
Port-forward band ho gaya hai. Dobara chalaao:
```powershell
kubectl port-forward svc/todo-frontend-service 3000:80
```

### Chat gives "Request failed with status 500"
OpenAI API key check karo:
```powershell
helm upgrade todo-backend charts/backend --set backend.openaiApiKey="YOUR-REAL-KEY"
kubectl rollout restart deployment todo-backend
```

### Release name already in use
```powershell
helm uninstall <release-name>
```

### Cluster unreachable / EOF error
```powershell
minikube stop
minikube start --cpus=2 --memory=3072 --driver=docker
```

---

## AI Tools Used

| Tool | Purpose | How Used |
|------|---------|----------|
| **Docker AI (Gordon)** | AI-assisted Docker operations | Analyzed & optimized frontend/backend Dockerfiles for security & performance |
| **kubectl-ai** | AI-assisted Kubernetes operations | Natural language pod management, health checks, resource monitoring |

See [AI-TOOLS-USAGE.md](AI-TOOLS-USAGE.md) for detailed usage evidence.

### Quick Commands
```powershell
# Gordon - Docker AI (no setup needed)
docker ai "analyze my Dockerfile for security issues" -C E:\hackathon-ii\Phase_4

# kubectl-ai (needs API key)
$env:OPENAI_API_KEY = "your-key"
E:\hackathon-ii\Phase_4\kubectl-ai-temp\kubectl-ai.exe "list all pods"
```

---

## Operational Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| Prerequisites check | Verify tools installed | `bash scripts/check-prerequisites.sh` |
| Smoke tests | 7 automated tests | `bash scripts/validate-deployment.sh` |
| Cleanup | Teardown all resources | `bash scripts/cleanup-deployment.sh` |
| Upgrade | Rolling upgrade | `bash scripts/upgrade-deployment.sh --component frontend --frontend-tag 2.1.0` |
| Rollback | Helm rollback | `bash scripts/rollback-deployment.sh --component backend` |

---

## Project Structure

```
Phase_4/
├── frontend/               # React TypeScript + Nginx
│   ├── src/               # Source code
│   ├── Dockerfile         # Multi-stage build
│   └── nginx.conf         # Nginx + API proxy config
├── backend/                # Python FastAPI
│   ├── src/               # Source code
│   ├── Dockerfile         # Python 3.11-slim build
│   └── requirements.txt   # Dependencies
├── charts/                 # Helm Charts
│   ├── frontend/          # Frontend chart (2 replicas)
│   ├── backend/           # Backend chart (1 replica)
│   └── database/          # PostgreSQL StatefulSet
├── scripts/                # Automation
│   ├── check-prerequisites.sh
│   ├── validate-deployment.sh
│   ├── cleanup-deployment.sh
│   ├── upgrade-deployment.sh
│   └── rollback-deployment.sh
└── specs/                  # Specifications & Planning
    └── 1-k8s-deployment/
        ├── spec.md
        ├── plan.md
        └── tasks.md
```

---

**Project**: Todo AI Chatbot
**Phase**: 4 - Kubernetes Deployment
**Last Updated**: 2026-02-07
