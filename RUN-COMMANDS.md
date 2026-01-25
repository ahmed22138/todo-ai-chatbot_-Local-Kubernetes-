# Phase 4 - Complete Run Commands & Video Guide

## Project Information

| Item | Value |
|------|-------|
| **Project Name** | Todo AI Chatbot |
| **Project Path** | `E:\hackathon-ii\Phase_4` |
| **Deployed On** | Local Kubernetes (Minikube) |
| **Platform** | Docker Desktop |
| **Access URL** | http://127.0.0.1:3000 |

---

## Deployment Architecture

```
Your Computer
    └── Docker Desktop (Container Runtime)
            └── Minikube (Kubernetes Cluster)
                    ├── todo-frontend (2 pods) - React + Nginx
                    ├── todo-backend (1 pod) - FastAPI + Python
                    └── todo-database (1 pod) - PostgreSQL 16
```

---

## Step-by-Step Run Commands

### Step 1: Start Docker Desktop
```
Windows Start Menu → Docker Desktop → Open
Wait until green icon shows "Docker Desktop is running"
```

### Step 2: Start Minikube
```bash
minikube start
```

### Step 3: Check Minikube Status
```bash
minikube status
```

**Expected Output:**
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

### Step 4: Check All Pods
```bash
kubectl get pods
```

**Expected Output:**
```
NAME                                        READY   STATUS    RESTARTS   AGE
todo-backend-xxx-xxx                        1/1     Running   0          1h
todo-database-0                             1/1     Running   0          1h
todo-frontend-deployment-xxx-xxx            1/1     Running   0          1h
```

### Step 5: Check All Services
```bash
kubectl get services
```

**Expected Output:**
```
NAME                     TYPE        CLUSTER-IP       PORT(S)
kubernetes               ClusterIP   10.96.0.1        443/TCP
todo-backend-service     NodePort    10.108.x.x       8000:30800/TCP
todo-database-service    ClusterIP   10.104.x.x       5432/TCP
todo-frontend-service    NodePort    10.105.x.x       80:30080/TCP
```

### Step 6: Check Helm Releases
```bash
helm list
```

**Expected Output:**
```
NAME            NAMESPACE   REVISION   STATUS     CHART
todo-backend    default     1          deployed   backend-0.1.0
todo-database   default     1          deployed   database-0.1.0
todo-frontend   default     1          deployed   frontend-0.1.0
```

### Step 7: Start Port Forward (Required for Access)
```bash
kubectl port-forward svc/todo-frontend-service 3000:80
```

**Note:** Keep this terminal open! Don't close it.

### Step 8: Open in Browser
```
http://127.0.0.1:3000
```

---

## Video Demonstration Script

### Scene 1: Docker Desktop (10 seconds)
- Show Docker Desktop is running
- Show the green whale icon in taskbar

### Scene 2: Terminal Commands (60 seconds)

Run these commands one by one:

```bash
# 1. Check Minikube Status
minikube status

# 2. Show All Pods
kubectl get pods

# 3. Show All Services
kubectl get services

# 4. Show Helm Releases
helm list

# 5. Show Docker Images
docker images | findstr todo
```

### Scene 3: Start Port Forward (10 seconds)
```bash
kubectl port-forward svc/todo-frontend-service 3000:80
```

### Scene 4: Browser Demo (60 seconds)
1. Open http://127.0.0.1:3000
2. Click "Create Account"
3. Register with name, email, password
4. Login with credentials
5. Type in chat: "Add a task to buy groceries"
6. Show task being added
7. Type: "List my tasks"
8. Show tasks being displayed

---

## All Commands (Copy-Paste Ready)

```bash
# Docker Version Check
docker --version

# Minikube Version Check
minikube version

# Helm Version Check
helm version

# Kubectl Version Check
kubectl version

# Start Minikube Cluster
minikube start

# Check Minikube Status
minikube status

# Check All Pods
kubectl get pods

# Check All Services
kubectl get services

# Check All Deployments
kubectl get deployments

# Check Helm Releases
helm list

# Check Docker Images
docker images | findstr todo

# Port Forward (Access App)
kubectl port-forward svc/todo-frontend-service 3000:80

# Check Backend Logs
kubectl logs deploy/todo-backend --tail=20

# Check Frontend Logs
kubectl logs deploy/todo-frontend-deployment --tail=20

# Check Database Logs
kubectl logs todo-database-0 --tail=20

# Describe a Pod
kubectl describe pod <pod-name>

# Stop Minikube
minikube stop

# Delete Minikube Cluster (Caution!)
minikube delete
```

---

## Docker Images

| Image Name | Tag | Description |
|------------|-----|-------------|
| `todo-frontend` | 2.0.8 | React + Nginx frontend |
| `todo-backend` | 1.0.0 | FastAPI + Python backend |
| `postgres` | 16-alpine | PostgreSQL database |

---

## Helm Charts (Deployment Packages)

| Chart Name | Location | Description |
|------------|----------|-------------|
| `frontend` | `charts/frontend/` | Frontend deployment config |
| `backend` | `charts/backend/` | Backend deployment config |
| `database` | `charts/database/` | PostgreSQL StatefulSet config |

---

## Services & Ports

| Service Name | Type | Internal Port | External Port | Description |
|--------------|------|---------------|---------------|-------------|
| todo-frontend-service | NodePort | 80 | 30080 | Frontend web server |
| todo-backend-service | NodePort | 8000 | 30800 | Backend API server |
| todo-database-service | ClusterIP | 5432 | - | PostgreSQL database |

---

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Container Platform | Docker Desktop | Latest |
| Container Orchestration | Minikube | v1.37.0 |
| Kubernetes | K8s | v1.28.0 |
| Package Manager | Helm | v4.0.3 |
| Frontend | React + TypeScript | 18.x |
| Build Tool | Vite | 5.x |
| Web Server | Nginx | 1.29.x |
| Backend | FastAPI | 0.100+ |
| Language | Python | 3.11 |
| Database | PostgreSQL | 16-alpine |
| AI Integration | OpenAI API | GPT-4 |

---

## Quick Start (3 Commands)

```bash
# 1. Start Minikube
minikube start

# 2. Check Pods are Running
kubectl get pods

# 3. Start Port Forward
kubectl port-forward svc/todo-frontend-service 3000:80
```

Then open: **http://127.0.0.1:3000**

---

## Troubleshooting

### Problem: Minikube not starting
```bash
# Restart Docker Desktop first, then:
minikube delete
minikube start
```

### Problem: Pods not running
```bash
# Check pod status
kubectl get pods

# If pod is in Error/CrashLoopBackOff, delete it
kubectl delete pod <pod-name>

# Kubernetes will automatically recreate it
```

### Problem: Port 3000 already in use
```bash
# Use a different port
kubectl port-forward svc/todo-frontend-service 4000:80

# Then open: http://127.0.0.1:4000
```

### Problem: "Failed to fetch" error
```bash
# Restart port-forward
# Press Ctrl+C to stop current one
kubectl port-forward svc/todo-frontend-service 3000:80

# Open in Incognito browser window
```

### Problem: Backend not connecting to database
```bash
# Restart backend pod
kubectl delete pod -l app=todo-backend

# Wait 30 seconds and check
kubectl get pods
```

---

## One-Line Summary (For Presentation)

> "This is a Todo AI Chatbot application built with React frontend, FastAPI backend, and PostgreSQL database, containerized with Docker and deployed on a local Kubernetes cluster (Minikube) using Helm Charts, with OpenAI integration for AI-powered task management."

---

## GitHub Repository

**URL:** https://github.com/ahmed22138/todo-ai-chatbot_-Local-Kubernetes-.git

**Branch:** `1-k8s-deployment`

---

## Contact

**Developer:** Ahmed Zahid
**Email:** ahmedzahid119@gmail.com

---

*Last Updated: January 2026*
