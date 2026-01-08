# Phase IV: Kubernetes Deployment Guidelines

Auto-generated from feature plan. Last updated: 2026-01-07

## Active Technologies

### Infrastructure & Orchestration
- **Kubernetes**: 1.28+ (via Minikube)
- **Minikube**: 1.32+ (local Kubernetes cluster)
- **Helm**: 3.12+ (package manager for Kubernetes)
- **Docker**: 20.10+ (container runtime)

### Container Images
- **Alpine Linux**: 3.18+ (minimal base image)
- **Nginx**: 1.25-alpine (static file serving for frontend)
- **Node.js**: 18-alpine (LTS, backend runtime)
- **MongoDB**: 7 (document database)

### AI Agent Stack
- **Docker AI Agent (Gordon)**: Dockerfile generation and image optimization
- **kubectl-ai**: Kubernetes deployment assistance and troubleshooting
- **kagent**: Cluster health analysis and resource optimization
- **Claude Sonnet 4.5** (20250929): Primary orchestrator for planning and coordination

### Development Tools
- **kubectl**: 1.28+ (Kubernetes CLI)
- **helm**: 3.x (chart management)
- **docker**: 20.10+ (image building and management)

---

## Project Structure

```text
Phase_4/
├── frontend/                    # React application source
│   ├── Dockerfile              # Multi-stage: Node.js builder + Nginx runtime
│   ├── src/                    # React components
│   ├── public/                 # Static assets
│   └── package.json            # NPM dependencies
│
├── backend/                     # Node.js API server source
│   ├── Dockerfile              # Multi-stage: Node.js builder + runtime
│   ├── src/                    # API routes, controllers, models
│   ├── server.js               # Entry point
│   └── package.json            # NPM dependencies
│
├── charts/                      # Helm charts for Kubernetes deployment
│   ├── frontend/
│   │   ├── Chart.yaml          # Chart metadata
│   │   ├── values.yaml         # Default configuration
│   │   ├── templates/
│   │   │   ├── deployment.yaml # Deployment resource (2 replicas)
│   │   │   ├── service.yaml    # Service resource (NodePort/ClusterIP)
│   │   │   ├── configmap.yaml  # Environment configuration
│   │   │   ├── _helpers.tpl    # Helm template helpers
│   │   │   └── NOTES.txt       # Post-install instructions
│   │   └── README.md           # Chart documentation
│   │
│   ├── backend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── templates/
│   │   │   ├── deployment.yaml # Deployment resource (1 replica)
│   │   │   ├── service.yaml    # Service resource (ClusterIP internal)
│   │   │   ├── configmap.yaml  # Non-sensitive config
│   │   │   ├── secret.yaml     # Sensitive config (DB credentials)
│   │   │   ├── _helpers.tpl
│   │   │   └── NOTES.txt
│   │   └── README.md
│   │
│   └── database/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── templates/
│       │   ├── statefulset.yaml # StatefulSet for MongoDB
│       │   ├── service.yaml     # ClusterIP (internal only)
│       │   ├── _helpers.tpl
│       │   └── NOTES.txt
│       └── README.md
│
├── scripts/                     # Deployment and validation scripts
│   ├── check-prerequisites.sh  # Verify Docker, Minikube, kubectl, Helm
│   └── validate-deployment.sh  # Smoke tests for deployed system
│
├── specs/                       # Feature specifications
│   └── 1-k8s-deployment/
│       ├── spec.md             # Feature specification
│       ├── plan.md             # Implementation plan
│       ├── research.md         # Technology decisions (Phase 0)
│       ├── data-model.md       # Kubernetes resource entities (Phase 1)
│       ├── quickstart.md       # Deployment guide (Phase 1)
│       ├── contracts/          # Helm chart specifications
│       │   └── helm-charts-specification.md
│       └── checklists/
│           └── requirements.md # Specification validation
│
├── .specify/                    # SpecKit Plus framework
│   ├── memory/
│   │   └── constitution.md     # Phase IV principles
│   ├── templates/              # Spec, plan, tasks templates
│   └── scripts/                # Automation scripts
│
├── history/                     # Prompt History Records (PHRs)
│   └── prompts/
│       ├── constitution/       # Constitution PHRs
│       └── 1-k8s-deployment/   # Feature-specific PHRs
│
└── CLAUDE.md                    # This file (agent context)
```

---

## Commands

### Minikube Cluster Management

```bash
# Start Minikube with recommended resources
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker

# Stop Minikube (preserves state)
minikube stop

# Delete Minikube cluster (removes all data)
minikube delete

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Get cluster info
minikube status
minikube ip
kubectl cluster-info
```

### Docker Image Management

```bash
# Build images
docker build -t todo-frontend:1.0.0 ./frontend
docker build -t todo-backend:1.0.0 ./backend

# Load images into Minikube
minikube image load todo-frontend:1.0.0
minikube image load todo-backend:1.0.0

# List images in Minikube
minikube image ls | grep todo-

# Use Minikube's Docker daemon (alternative)
eval $(minikube docker-env)
docker build -t todo-frontend:1.0.0 ./frontend
eval $(minikube docker-env --unset)
```

### Helm Chart Operations

```bash
# Lint charts
helm lint charts/frontend
helm lint charts/backend
helm lint charts/database

# Dry-run template rendering
helm template frontend charts/frontend
helm install --dry-run --debug frontend charts/frontend

# Install charts (in order: database → backend → frontend)
helm install todo-database charts/database
helm install todo-backend charts/backend
helm install todo-frontend charts/frontend

# List installed releases
helm list

# Upgrade release
helm upgrade todo-frontend charts/frontend --set image.tag=1.0.1

# Rollback release
helm rollback todo-frontend
helm rollback todo-frontend 2  # Specific revision

# Uninstall releases
helm uninstall todo-frontend
helm uninstall todo-backend
helm uninstall todo-database

# View release history
helm history todo-frontend
helm status todo-frontend
```

### Kubernetes Resource Management

```bash
# Get resources
kubectl get pods
kubectl get deployments
kubectl get services
kubectl get statefulsets
kubectl get pvc  # PersistentVolumeClaims
kubectl get ingress

# Describe resources (detailed info + events)
kubectl describe pod <pod-name>
kubectl describe service <service-name>
kubectl describe deployment <deployment-name>

# Check pod logs
kubectl logs <pod-name>
kubectl logs -l app.kubernetes.io/name=frontend --tail=50 -f
kubectl logs todo-database-0 --tail=50

# Wait for condition
kubectl wait --for=condition=ready pod --all --timeout=120s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=backend --timeout=120s

# Execute commands in pod
kubectl exec -it <pod-name> -- /bin/sh
kubectl exec -it deployment/todo-backend-deployment -- curl http://localhost:5000/health

# Port forwarding
kubectl port-forward svc/todo-frontend-service 8080:80
kubectl port-forward svc/todo-backend-service 5000:5000

# Resource utilization
kubectl top nodes
kubectl top pods

# Scale deployment
kubectl scale deployment todo-frontend-deployment --replicas=3

# Rollout management
kubectl rollout status deployment/todo-frontend-deployment
kubectl rollout history deployment/todo-frontend-deployment
kubectl rollout undo deployment/todo-frontend-deployment
```

### kubectl-ai Commands (if available)

```bash
# Deployment assistance
kubectl-ai "deploy frontend with 2 replicas using image todo-frontend:1.0.0"
kubectl-ai "expose frontend deployment on port 80 as NodePort"

# Troubleshooting
kubectl-ai "why is my backend pod not starting?"
kubectl-ai "analyze pod errors in namespace default"
kubectl-ai "test connectivity from frontend to backend-service:5000"

# Resource queries
kubectl-ai "show pods using most memory"
kubectl-ai "list all services and their endpoints"
```

### kagent Commands (if available)

```bash
# Cluster analysis
kagent analyze cluster        # Overall health
kagent analyze resources      # Resource utilization and rightsizing
kagent audit security         # Security best practices

# Deployment validation
kagent analyze deployment frontend
kagent analyze scheduling
kagent diagnose failures

# Network analysis
kagent analyze network
```

### Docker AI Agent (Gordon) Commands (if available)

```bash
# Generate Dockerfile
docker ai generate dockerfile \
  --context ./frontend \
  --output ./frontend/Dockerfile \
  --base-image node:18-alpine \
  --multi-stage \
  --runtime nginx:alpine

# Optimize existing Dockerfile
docker ai optimize dockerfile ./backend/Dockerfile
```

---

## Code Style

### Dockerfile Best Practices

- **Multi-stage builds**: Separate builder and runtime stages
- **Alpine base images**: Minimize image size and attack surface
- **Non-root user**: Run containers as non-root for security
- **Layer caching**: Order commands to maximize cache reuse (COPY package.json before source code)
- **Explicit versions**: Never use `latest` tags; specify versions (e.g., `node:18-alpine`)
- **.dockerignore**: Exclude unnecessary files (node_modules, .git, .env)
- **Health checks**: Define HEALTHCHECK instruction for probes

**Frontend Dockerfile Pattern**:
```dockerfile
# Stage 1: Builder
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
USER nginx
CMD ["nginx", "-g", "daemon off;"]
```

**Backend Dockerfile Pattern**:
```dockerfile
# Stage 1: Builder
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

# Stage 2: Runtime
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/src ./src
COPY --from=builder /app/server.js ./
EXPOSE 5000
USER node
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:5000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"
CMD ["node", "server.js"]
```

### Helm Template Best Practices

- **Use _helpers.tpl**: Define reusable template functions for labels, names, selectors
- **Parameterize everything**: All hardcoded values should be in values.yaml
- **Checksums for config**: Annotate pods with config/secret checksums to force restarts on changes
- **Resource limits**: Always define requests and limits in values.yaml
- **Health probes**: Liveness and readiness probes mandatory for all deployments
- **Semantic versioning**: Chart version and appVersion follow SemVer
- **Documentation**: README.md for each chart; NOTES.txt for post-install instructions

**values.yaml Pattern**:
```yaml
replicaCount: 2

image:
  repository: todo-frontend
  tag: 1.0.0
  pullPolicy: IfNotPresent

service:
  type: NodePort
  port: 80

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi

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
```

### Kubernetes Manifest Best Practices

- **Labels**: Use standard labels (app.kubernetes.io/name, app.kubernetes.io/instance, app.kubernetes.io/version)
- **Selectors**: Deployment selectors must match pod template labels
- **Rolling updates**: Use RollingUpdate strategy with maxUnavailable: 0, maxSurge: 1
- **Image pull policy**: IfNotPresent for local images (avoid pulling from registry)
- **Service types**: ClusterIP for internal services, NodePort for external (or ClusterIP + Ingress)
- **StatefulSet for state**: Use StatefulSet (not Deployment) for databases requiring persistence
- **PVC retention**: StatefulSet PVCs persist after deletion; delete manually to remove data

---

## Recent Changes

### Feature 1: Phase IV Constitution (2026-01-07)
- Established seven core principles for Kubernetes deployment
- Defined Agentic Dev Stack (Gordon, kubectl-ai, kagent, Claude)
- Documented cloud-native best practices and Minikube-first approach
- Set REE requirements (Reproducible, Explainable, Evaluatable)
- Constitution version: 1.0.0

### Feature 2: Cloud-Native Kubernetes Deployment Specification (2026-01-07)
- Four prioritized user stories (P1: Cluster setup, P2: Backend, P3: Frontend, P4: Validation)
- 15 functional requirements (FR-001 to FR-015) for containerization and deployment
- 6 operational requirements (OR-001 to OR-006) for AI agent integration
- 8 measurable success criteria (SC-001 to SC-008) with specific targets
- Specification validated with 16/16 quality checklist items passing

### Feature 3: Implementation Plan and Design Artifacts (2026-01-07)
- Phase 0 Research: Technology decisions for Docker, Kubernetes, Helm, AI agents
- Phase 1 Data Model: Kubernetes resource entities (Deployment, Service, StatefulSet, PVC, ConfigMap, Secret, Ingress, Helm Release)
- Phase 1 Contracts: Helm chart specifications with template structure and values.yaml schemas
- Phase 1 Quickstart: Step-by-step deployment guide with kubectl-ai and kagent commands
- Added: Multi-stage Docker builds with Alpine, Helm charts for frontend/backend/database, smoke test validation

---

<!-- MANUAL ADDITIONS START -->
<!-- Add any project-specific guidance, conventions, or constraints here -->
<!-- This section is preserved across agent context updates -->
<!-- MANUAL ADDITIONS END -->
