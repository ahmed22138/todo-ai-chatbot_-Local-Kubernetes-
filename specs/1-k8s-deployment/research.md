# Phase 0: Research - Kubernetes Deployment Strategy

**Feature**: Cloud-Native Kubernetes Deployment
**Branch**: `1-k8s-deployment`
**Date**: 2026-01-07
**Status**: Complete

## Purpose

This document captures research findings for deploying the Phase III Todo AI Chatbot to a local Kubernetes cluster using the Agentic Dev Stack. All technology decisions and best practices are documented here to resolve unknowns before implementation.

---

## Research Areas

### 1. Docker Containerization Strategy

**Decision**: Multi-stage Docker builds with Alpine base images for production containers

**Rationale**:
- **Multi-stage builds**: Separate build and runtime stages minimize final image size (build tools excluded from production image)
- **Alpine Linux**: Lightweight base (~5MB) reduces attack surface and speeds up image pulls
- **Layer caching**: Dependency installation layers cached separately from application code for faster rebuilds

**Alternatives Considered**:
- **Single-stage builds**: Simpler but includes unnecessary build tools in production image (rejected: security and size concerns)
- **Debian/Ubuntu base**: More familiar but 10x larger than Alpine (rejected: unnecessary bloat for Node.js/React apps)
- **Distroless images**: Minimal attack surface but harder to debug (deferred: adds complexity for Phase IV)

**Best Practices Applied**:
- Non-root user in containers (security)
- `.dockerignore` to exclude unnecessary files
- Explicit version tags (no `latest`)
- Health check instructions in Dockerfile
- Minimal layer count (combine RUN commands)

**Agent Responsibility**: Docker AI Agent (Gordon) for Dockerfile generation

---

### 2. Frontend Containerization (React Application)

**Decision**: Nginx-based static file serving with build-time environment variable injection

**Rationale**:
- **Nginx**: Industry-standard static file server; lightweight (~20MB); excellent performance
- **Build-time configuration**: Frontend built with backend API URL baked in via environment variables
- **Two-stage approach**: Stage 1 (Node.js builder) compiles React; Stage 2 (Nginx) serves static files

**Dockerfile Structure**:
```
Stage 1: Builder (node:18-alpine)
- Install dependencies (npm ci)
- Build React app (npm run build)
- Output to /app/build

Stage 2: Runtime (nginx:alpine)
- Copy build artifacts from Stage 1
- Copy custom nginx.conf for SPA routing
- Expose port 80 (not 3000; Nginx serves on 80)
- Non-root user (nginx user)
```

**Configuration Management**:
- **Backend API URL**: Injected at build time via `REACT_APP_BACKEND_URL` environment variable
- **Kubernetes ConfigMap**: Provides `REACT_APP_BACKEND_URL=http://backend-service:5000` (internal cluster DNS)
- **Helm templating**: ConfigMap values rendered from `values.yaml`

**Alternatives Considered**:
- **Node.js server for serving**: Unnecessary; Nginx is optimized for static files (rejected: overhead)
- **Runtime environment variable injection**: Requires custom script; adds complexity (rejected: build-time sufficient for local deployment)

**Image Tag**: `todo-frontend:1.0.0`

---

### 3. Backend Containerization (Node.js API)

**Decision**: Node.js Alpine-based container with production dependencies only

**Rationale**:
- **Node.js 18 Alpine**: LTS version; minimal base image
- **Production dependencies only**: `npm ci --only=production` excludes dev dependencies (smaller image)
- **Environment-based configuration**: Database URL, API keys from environment variables (12-factor app)

**Dockerfile Structure**:
```
Stage 1: Builder (node:18-alpine)
- Install all dependencies (npm ci)
- Run any build steps (TypeScript compilation if applicable)

Stage 2: Runtime (node:18-alpine)
- Copy production dependencies only
- Copy application code
- Non-root user (node user)
- Expose port 5000
- Health check on /health endpoint
- CMD ["node", "server.js"]
```

**Configuration Management**:
- **Database URL**: Provided via Kubernetes Secret (e.g., `MONGODB_URI`)
- **Environment variables**: ConfigMap for non-sensitive config (e.g., `NODE_ENV=production`)
- **Secrets**: Kubernetes Secret for sensitive data (database credentials, API keys)

**Health Checks**:
- **Liveness probe**: GET /health (ensures server is responsive)
- **Readiness probe**: GET /ready (checks database connectivity before receiving traffic)

**Alternatives Considered**:
- **Include dev dependencies**: Simpler but 2-3x larger image (rejected: unnecessary in production)
- **PM2 process manager**: Adds complexity; Kubernetes handles restarts (rejected: YAGNI for single-instance deployment)

**Image Tag**: `todo-backend:1.0.0`

---

### 4. Docker AI Agent (Gordon) Integration

**Decision**: Use Gordon for Dockerfile generation with fallback to Claude-generated Dockerfiles

**Rationale**:
- **Gordon specialization**: Docker AI Agent optimized for Dockerfile best practices
- **Fallback strategy**: If Gordon unavailable, Claude Sonnet 4.5 generates Dockerfiles following Gordon's patterns

**Gordon Invocation Pattern**:
```bash
# Frontend Dockerfile generation
docker ai generate dockerfile \
  --context frontend/ \
  --output frontend/Dockerfile \
  --base-image node:18-alpine \
  --multi-stage \
  --runtime nginx:alpine

# Backend Dockerfile generation
docker ai generate dockerfile \
  --context backend/ \
  --output backend/Dockerfile \
  --base-image node:18-alpine \
  --multi-stage \
  --health-check /health
```

**Validation**:
- Gordon outputs must be reviewed for security best practices
- Validate with `docker build` (ensure no errors)
- Check image size (frontend <50MB, backend <100MB targets)

**Fallback (Gordon Unavailable)**:
- Claude generates Dockerfiles following multi-stage, Alpine, non-root user patterns
- Manual review against Dockerfile linting rules (hadolint)

---

### 5. Local Image Availability for Minikube

**Decision**: Load Docker images directly into Minikube's Docker daemon

**Rationale**:
- **No registry required**: Minikube can use images from its internal Docker daemon
- **Fast iteration**: No push/pull from external registry
- **Local development**: Simplifies workflow for Phase IV

**Implementation Strategy**:

**Option A: Load images into Minikube (Recommended)**
```bash
# Build images on host Docker daemon
docker build -t todo-frontend:1.0.0 frontend/
docker build -t todo-backend:1.0.0 backend/

# Load into Minikube
minikube image load todo-frontend:1.0.0
minikube image load todo-backend:1.0.0
```

**Option B: Use Minikube's Docker daemon directly**
```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Build images directly in Minikube
docker build -t todo-frontend:1.0.0 frontend/
docker build -t todo-backend:1.0.0 backend/
```

**Chosen Approach**: Option A (load images) for clarity and avoiding Docker environment conflicts

**Helm Chart Configuration**:
- `imagePullPolicy: IfNotPresent` (use local images, don't pull from registry)
- `image.repository: todo-frontend` and `image.tag: 1.0.0` in values.yaml

**Alternatives Considered**:
- **Local Docker registry in Minikube**: Adds complexity; unnecessary for local dev (rejected: YAGNI)
- **Docker Hub public registry**: Requires authentication; slow for iteration (rejected: not suitable for Phase IV)

---

### 6. Helm Chart Architecture

**Decision**: Three independent Helm charts with umbrella chart optional

**Rationale**:
- **Separation of concerns**: Frontend, backend, database as independent charts
- **Independent lifecycle**: Each service can be installed, upgraded, rolled back independently
- **Reusability**: Charts can be packaged and shared

**Chart Structure**:

```
charts/
├── frontend/
│   ├── Chart.yaml              # Chart metadata (name, version, description)
│   ├── values.yaml             # Default configuration values
│   ├── templates/
│   │   ├── deployment.yaml     # Deployment resource
│   │   ├── service.yaml        # Service resource (ClusterIP or NodePort)
│   │   ├── configmap.yaml      # Environment configuration
│   │   ├── _helpers.tpl        # Helm template helpers
│   │   └── NOTES.txt           # Post-install instructions
│   └── README.md               # Chart documentation
│
├── backend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml        # ClusterIP (internal only)
│   │   ├── configmap.yaml
│   │   ├── secret.yaml         # Database credentials
│   │   ├── _helpers.tpl
│   │   └── NOTES.txt
│   └── README.md
│
└── database/
    ├── Chart.yaml
    ├── values.yaml
    ├── templates/
    │   ├── statefulset.yaml    # StatefulSet for persistence
    │   ├── service.yaml        # ClusterIP (internal only)
    │   ├── pvc.yaml            # PersistentVolumeClaim
    │   ├── _helpers.tpl
    │   └── NOTES.txt
    └── README.md
```

**Helm Values Structure** (example for backend):
```yaml
replicaCount: 1
image:
  repository: todo-backend
  tag: 1.0.0
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 5000
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi
env:
  NODE_ENV: production
secret:
  mongodbUri: mongodb://mongodb-service:27017/todos
```

**Alternatives Considered**:
- **Single monolithic chart**: Simpler but tight coupling; hard to version independently (rejected: violates separation of concerns)
- **Umbrella chart**: Parent chart that installs all subcharts; useful but adds complexity (deferred: optional for Phase IV)
- **Kustomize instead of Helm**: Less mature ecosystem; no release management (rejected: Helm preferred per constitution)

**Chart Versioning**:
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Initial version: 0.1.0 (pre-release)
- Increment PATCH for bug fixes, MINOR for new features, MAJOR for breaking changes

---

### 7. Kubernetes Deployment Strategy

**Decision**: Rolling update deployments with readiness gates; StatefulSet for database

**Rationale**:
- **Rolling updates**: Zero-downtime deployments; Kubernetes default strategy
- **Readiness probes**: Ensure new pods are healthy before routing traffic
- **StatefulSet for database**: Stable network identity; ordered deployment for persistence

**Deployment Configuration** (Frontend & Backend):

```yaml
spec:
  replicas: 2  # Frontend (configurable via values.yaml)
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0    # Always maintain at least 1 replica
      maxSurge: 1          # Add 1 new pod before terminating old
  template:
    spec:
      containers:
      - name: frontend
        image: todo-frontend:1.0.0
        ports:
        - containerPort: 80
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
```

**Service Configuration**:

- **Frontend Service**: Type `NodePort` (external access) or `ClusterIP` + Ingress
- **Backend Service**: Type `ClusterIP` (internal only, accessed via DNS: `backend-service:5000`)
- **Database Service**: Type `ClusterIP` (internal only, accessed via DNS: `mongodb-service:27017`)

**Database Persistence**:
- **StatefulSet**: Ordered pod creation; stable pod names (mongodb-0, mongodb-1, etc.)
- **PersistentVolumeClaim**: Requested storage (e.g., 5Gi)
- **StorageClass**: Minikube default `standard` (hostPath-based local storage)

**Alternatives Considered**:
- **Recreate strategy**: Simpler but causes downtime (rejected: zero-downtime required)
- **Blue-green deployment**: More complex; requires duplicate resources (deferred: overkill for Phase IV)
- **Deployment for database**: Loses data on pod restart (rejected: StatefulSet required for persistence)

---

### 8. kubectl-ai Integration for Deployment & Troubleshooting

**Decision**: Use kubectl-ai for AI-assisted deployment commands and troubleshooting

**Rationale**:
- **Natural language queries**: Simplifies complex kubectl operations
- **Error diagnosis**: AI interprets error messages and suggests fixes
- **Best practices**: kubectl-ai suggests optimal kubectl commands

**kubectl-ai Usage Patterns**:

**Deployment Assistance**:
```bash
# Generate deployment command
kubectl-ai "deploy frontend with 2 replicas using image todo-frontend:1.0.0"
# Output: kubectl create deployment frontend --image=todo-frontend:1.0.0 --replicas=2

# Create service with NodePort
kubectl-ai "expose frontend deployment on port 80 as NodePort"
# Output: kubectl expose deployment frontend --type=NodePort --port=80

# Check pod status
kubectl-ai "why is my frontend pod not starting?"
# Output: Runs kubectl describe pod <pod-name> and interprets CrashLoopBackOff errors
```

**Troubleshooting Assistance**:
```bash
# Diagnose pod issues
kubectl-ai "analyze pod errors in namespace default"
# Output: Checks logs, events, describes pods with issues

# Network debugging
kubectl-ai "test connectivity from frontend to backend-service:5000"
# Output: Creates debug pod, runs curl command, reports results

# Resource issues
kubectl-ai "show pods using most memory"
# Output: kubectl top pods --sort-by=memory
```

**Integration Points**:
- **Post-deployment validation**: Use kubectl-ai to verify deployments
- **Error diagnosis**: When Helm install fails, use kubectl-ai to interpret errors
- **Documentation**: Include kubectl-ai commands in quickstart.md

**Fallback**: If kubectl-ai unavailable, use standard kubectl commands (documented in quickstart.md)

---

### 9. kagent Integration for Cluster Analysis

**Decision**: Use kagent for Kubernetes cluster health analysis and resource optimization

**Rationale**:
- **Cluster-wide insights**: Analyzes resource utilization, misconfigurations, best practices
- **Proactive recommendations**: Identifies issues before they cause failures
- **Security auditing**: Checks for common security misconfigurations

**kagent Usage Patterns**:

**Cluster Health Check**:
```bash
# Overall cluster health
kagent analyze cluster
# Output: Reports on node health, resource usage, addon status

# Resource utilization
kagent analyze resources
# Output: CPU/memory usage across nodes and pods; suggests rightsizing

# Security audit
kagent audit security
# Output: Checks for privileged containers, missing resource limits, exposed secrets
```

**Deployment Validation**:
```bash
# Validate deployments follow best practices
kagent analyze deployment frontend
# Output: Checks for health probes, resource limits, labels, annotations

# Analyze pod scheduling
kagent analyze scheduling
# Output: Reports on pod affinity, node selection, resource constraints
```

**Troubleshooting**:
```bash
# Identify failing pods and root causes
kagent diagnose failures
# Output: Lists failing pods with categorized errors (image pull, crash loop, OOM)

# Network policy validation
kagent analyze network
# Output: Checks service reachability, DNS resolution, network policies
```

**Integration Points**:
- **Pre-deployment**: Run `kagent analyze cluster` to ensure cluster is healthy
- **Post-deployment**: Run `kagent analyze deployment` to validate best practices
- **Continuous monitoring**: Run `kagent analyze resources` to track utilization

**Fallback**: If kagent unavailable, use standard kubectl commands (kubectl get, describe, logs, top)

---

### 10. Validation & Verification Strategy

**Decision**: Multi-layered validation with automated smoke tests

**Rationale**:
- **Layered approach**: Validate at multiple stages (pre-deployment, deployment, post-deployment)
- **Automation**: Reduce manual verification; enable reproducibility
- **Fast feedback**: Detect issues early in deployment pipeline

**Validation Layers**:

**Layer 1: Pre-Deployment Validation**
- Helm chart linting: `helm lint charts/frontend`, `helm lint charts/backend`, `helm lint charts/database`
- Dockerfile validation: `docker build --check` or hadolint linting
- Kubernetes manifest validation: `kubectl apply --dry-run=client -f <manifest>`
- Cluster health check: `kagent analyze cluster` or `kubectl get nodes`

**Layer 2: Deployment Validation**
- Helm install dry-run: `helm install --dry-run --debug <release> <chart>`
- Template rendering check: `helm template <chart>` (verify YAML validity)
- Namespace readiness: Ensure namespace exists or create with `kubectl create namespace <ns>`

**Layer 3: Post-Deployment Validation**
- Pod status check: `kubectl get pods --all-namespaces` (all should be "Running")
- Service endpoints: `kubectl get endpoints` (ensure services have endpoints)
- Health probe validation: `kubectl get pods -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}'`
- Log inspection: `kubectl logs <pod-name>` (check for startup errors)

**Layer 4: End-to-End Smoke Tests**

**Smoke Test Script** (`scripts/validate-deployment.sh`):
```bash
#!/bin/bash
set -e

echo "=== Phase IV Deployment Validation ==="

# 1. Check cluster is running
echo "[1/7] Checking Minikube cluster..."
kubectl cluster-info || { echo "ERROR: Cluster not running"; exit 1; }

# 2. Check all pods are running
echo "[2/7] Checking pod status..."
kubectl wait --for=condition=ready pod --all --timeout=120s

# 3. Check frontend is accessible
echo "[3/7] Testing frontend accessibility..."
FRONTEND_URL=$(minikube service frontend-service --url)
curl -f $FRONTEND_URL || { echo "ERROR: Frontend not accessible"; exit 1; }

# 4. Check backend internal service
echo "[4/7] Testing backend service..."
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl -f http://backend-service:5000/health || { echo "ERROR: Backend not healthy"; exit 1; }

# 5. Test database connectivity
echo "[5/7] Testing database connectivity..."
kubectl run -it --rm mongo-test --image=mongo:7 --restart=Never -- \
  mongosh mongodb-service:27017/todos --eval "db.adminCommand('ping')" || \
  { echo "ERROR: Database not accessible"; exit 1; }

# 6. Run basic CRUD test
echo "[6/7] Testing CRUD operations..."
# POST /todos
curl -X POST -H "Content-Type: application/json" \
  -d '{"title":"Test Todo","completed":false}' \
  http://backend-service:5000/todos
# GET /todos
curl -f http://backend-service:5000/todos || { echo "ERROR: CRUD test failed"; exit 1; }

# 7. Resource utilization check
echo "[7/7] Checking resource utilization..."
kubectl top nodes
kubectl top pods

echo "=== All validation checks passed ==="
```

**Validation Metrics**:
- **Deployment success rate**: 100% of services should deploy without errors
- **Pod startup time**: All pods "Running" within 2 minutes (per SC-002)
- **Health check pass rate**: >99% over 5-minute observation period
- **Smoke test pass rate**: 100% of tests pass

**Alternatives Considered**:
- **Manual validation**: Error-prone; not reproducible (rejected: automation required)
- **Integration test suite**: Comprehensive but time-consuming for Phase IV (deferred: smoke tests sufficient)
- **GitOps validation**: Requires ArgoCD/Flux; out of scope (deferred: future phase)

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Base OS** | Alpine Linux | 3.18+ | Minimal attack surface, small image size |
| **Frontend Runtime** | Nginx | 1.25-alpine | Static file serving, lightweight |
| **Backend Runtime** | Node.js | 18-alpine | LTS support, Alpine-based |
| **Database** | MongoDB | 7 | Document store, community edition |
| **Container Engine** | Docker | 20.10+ | Industry standard, Gordon integration |
| **Orchestration** | Kubernetes | 1.28+ (Minikube) | Cloud-native standard |
| **Package Manager** | Helm | 3.x | Chart-based deployments |
| **AI Agents** | Gordon, kubectl-ai, kagent | Latest | Agentic Dev Stack |
| **Orchestrator Agent** | Claude Sonnet 4.5 | 20250929 | Planning and coordination |

---

## Dependencies & Prerequisites

**Phase III Deliverables** (Assumed Complete):
- Frontend React application (source code in `frontend/`)
- Backend Node.js API (source code in `backend/`)
- Database schema and seed data
- Environment configuration files (`.env.example`)

**Local Development Environment**:
- Docker Desktop 4.x+ (with Docker AI Agent Gordon if available)
- Minikube 1.32+ (with kubectl 1.28+)
- Helm 3.12+
- kubectl-ai (optional but recommended)
- kagent (optional but recommended)

**Minikube Addons Required**:
- `ingress` (Nginx Ingress Controller)
- `metrics-server` (for `kubectl top` commands)

**Minikube Configuration**:
- Driver: docker (recommended) or hyperkit/hyperv
- CPUs: 2+ (4 recommended)
- Memory: 4GB+ (8GB recommended)
- Disk: 20GB+

---

## Open Questions & Clarifications

**Status**: All unknowns resolved. No open questions remaining.

**Resolved During Research**:
1. ✅ **Dockerfile generation approach**: Gordon with Claude fallback
2. ✅ **Image registry strategy**: Load images directly into Minikube
3. ✅ **Frontend environment variables**: Build-time injection via ConfigMap
4. ✅ **Backend secrets management**: Kubernetes Secrets
5. ✅ **Database persistence**: StatefulSet with PVC on Minikube local storage
6. ✅ **Service exposure**: Frontend via NodePort/Ingress; Backend/DB internal ClusterIP
7. ✅ **Health check implementation**: HTTP probes on /health endpoints
8. ✅ **Validation strategy**: Multi-layered with automated smoke tests

---

## Next Steps

Phase 0 research is **COMPLETE**. Proceed to **Phase 1: Design & Contracts** to generate:

1. **data-model.md**: Entity definitions for Kubernetes resources (Deployments, Services, ConfigMaps, Secrets, PVCs)
2. **contracts/**: Helm chart values.yaml schemas and template documentation
3. **quickstart.md**: Step-by-step deployment guide with kubectl-ai and kagent commands
4. **Agent context update**: Add Kubernetes/Helm/Docker stack to agent-specific context file

---

**Research Completed By**: Claude Sonnet 4.5 (Orchestrator Agent)
**Date**: 2026-01-07
**Validated Against**: Phase IV Constitution v1.0.0
