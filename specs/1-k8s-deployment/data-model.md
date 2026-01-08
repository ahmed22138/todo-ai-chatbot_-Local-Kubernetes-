# Phase 1: Data Model - Kubernetes Resources

**Feature**: Cloud-Native Kubernetes Deployment
**Branch**: `1-k8s-deployment`
**Date**: 2026-01-07
**Status**: Complete

## Purpose

This document defines the Kubernetes resource entities and their relationships for deploying the Todo AI Chatbot to a local Minikube cluster. Unlike traditional data models focused on application entities, this data model describes infrastructure-as-code entities.

---

## Kubernetes Resource Entities

### 1. Deployment Resource

**Purpose**: Manages replica sets and pod lifecycle for stateless applications (Frontend, Backend)

**Attributes**:
- `metadata.name`: Deployment identifier (e.g., "frontend-deployment", "backend-deployment")
- `metadata.namespace`: Kubernetes namespace (default: "default")
- `metadata.labels`: Key-value pairs for resource organization (e.g., `app: frontend`, `tier: web`)
- `spec.replicas`: Desired number of pod replicas (Frontend: 2, Backend: 1)
- `spec.selector`: Label selector matching pod template (e.g., `app: frontend`)
- `spec.strategy`: Update strategy (RollingUpdate with maxUnavailable: 0, maxSurge: 1)
- `spec.template`: Pod template specification (containers, volumes, probes)

**Relationships**:
- **Manages**: ReplicaSet (1 Deployment → 1+ ReplicaSets over time)
- **Creates**: Pods (1 Deployment → N Pods where N = replicas)
- **References**: ConfigMap (for environment variables)
- **References**: Secret (for sensitive configuration)
- **Targeted by**: Service (for network exposure)

**Validation Rules**:
- `replicas` must be >= 1
- `selector` must match `template.metadata.labels`
- At least one container defined in `template.spec.containers`
- Resource requests/limits must be specified
- Liveness and readiness probes must be defined

**State Transitions**:
- Progressing → Available (rollout succeeds)
- Progressing → Failed (rollout fails due to image pull errors, crash loops)
- Available → Progressing (new rollout triggered by image/config change)

---

### 2. Service Resource

**Purpose**: Provides stable network endpoint for pod access (ClusterIP, NodePort, LoadBalancer)

**Attributes**:
- `metadata.name`: Service identifier (e.g., "frontend-service", "backend-service", "mongodb-service")
- `metadata.namespace`: Kubernetes namespace
- `metadata.labels`: Key-value pairs for organization
- `spec.type`: Service type (ClusterIP for internal, NodePort for external, LoadBalancer for Minikube tunnel)
- `spec.selector`: Label selector targeting pods (e.g., `app: backend`)
- `spec.ports`: Port mappings (port, targetPort, nodePort, protocol)
- `spec.clusterIP`: Automatically assigned internal IP (immutable after creation)

**Relationships**:
- **Targets**: Pods (1 Service → N Pods via label selector)
- **Referenced by**: Ingress (for HTTP routing)
- **Referenced by**: Other Services (via DNS: `<service-name>.<namespace>.svc.cluster.local`)

**Validation Rules**:
- `selector` must match at least one pod
- `spec.ports[*].targetPort` must match container port
- NodePort must be in range 30000-32767 (if type=NodePort)
- `type=ClusterIP` for internal services (backend, database)
- `type=NodePort` or `ClusterIP+Ingress` for external services (frontend)

**Service Types by Component**:
| Component | Service Type | Port | TargetPort | Accessibility |
|-----------|-------------|------|------------|---------------|
| Frontend | NodePort or ClusterIP | 80 | 80 (nginx) | External (via NodePort or Ingress) |
| Backend | ClusterIP | 5000 | 5000 (node) | Internal only (`backend-service:5000`) |
| MongoDB | ClusterIP | 27017 | 27017 | Internal only (`mongodb-service:27017`) |

---

### 3. StatefulSet Resource

**Purpose**: Manages stateful applications requiring stable network identity and persistent storage (MongoDB)

**Attributes**:
- `metadata.name`: StatefulSet identifier (e.g., "mongodb")
- `metadata.namespace`: Kubernetes namespace
- `spec.serviceName`: Headless service name for stable network IDs
- `spec.replicas`: Number of stateful pods (typically 1 for Phase IV; 3 for replication)
- `spec.selector`: Label selector matching pod template
- `spec.volumeClaimTemplates`: PVC template for each pod's persistent volume
- `spec.template`: Pod template (containers, volumes, probes)

**Relationships**:
- **Creates**: Pods with ordinal names (mongodb-0, mongodb-1, ..., mongodb-N)
- **Manages**: PersistentVolumeClaims (1 PVC per pod per volumeClaimTemplate)
- **Requires**: StorageClass (for dynamic PV provisioning)
- **Targeted by**: Headless Service (for stable DNS: `mongodb-0.mongodb-service.default.svc.cluster.local`)

**Validation Rules**:
- `serviceName` must reference existing headless service (clusterIP: None)
- `volumeClaimTemplates` must specify storageClassName
- Ordered pod creation/deletion (mongodb-0 before mongodb-1)
- Pod names are stable and persist across restarts

**State Transitions**:
- Creating → Running (pod provisioned, PVC bound, container started)
- Running → Terminating (pod deletion triggered)
- Terminating → Creating (pod recreated with same name and PVC)

---

### 4. PersistentVolumeClaim (PVC) Resource

**Purpose**: Requests persistent storage for stateful applications

**Attributes**:
- `metadata.name`: PVC identifier (auto-generated by StatefulSet: `data-mongodb-0`)
- `metadata.namespace`: Kubernetes namespace
- `spec.accessModes`: Access mode (`ReadWriteOnce` for single-node RW, `ReadOnlyMany`, `ReadWriteMany`)
- `spec.resources.requests.storage`: Storage size (e.g., "5Gi")
- `spec.storageClassName`: StorageClass name (Minikube default: "standard")
- `status.phase`: Pending → Bound (when PV assigned)

**Relationships**:
- **Created by**: StatefulSet (via volumeClaimTemplates) or manually
- **Bound to**: PersistentVolume (1 PVC → 1 PV)
- **Mounted by**: Pod (as volume)

**Validation Rules**:
- `requests.storage` must be positive integer with units (Mi, Gi, Ti)
- `accessModes` must be supported by StorageClass
- PVC remains even if StatefulSet is deleted (manual cleanup required)

**Minikube StorageClass**:
- **Name**: "standard"
- **Provisioner**: `k8s.io/minikube-hostpath`
- **Reclaim Policy**: Delete (PV deleted when PVC deleted)
- **Volume Binding Mode**: Immediate

---

### 5. ConfigMap Resource

**Purpose**: Stores non-sensitive configuration data as key-value pairs or files

**Attributes**:
- `metadata.name`: ConfigMap identifier (e.g., "frontend-config", "backend-config")
- `metadata.namespace`: Kubernetes namespace
- `data`: Key-value pairs of configuration (e.g., `NODE_ENV: "production"`)
- `binaryData`: Base64-encoded binary data (optional)

**Relationships**:
- **Referenced by**: Deployment/StatefulSet (as environment variables or mounted files)
- **Injected into**: Pods (at creation time, not updated dynamically)

**Validation Rules**:
- Keys must be valid environment variable names (alphanumeric + underscore)
- Total size limit: 1MiB per ConfigMap
- Immutable once created (modifications require pod restart to take effect)

**ConfigMap Examples**:

**Frontend ConfigMap**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
data:
  REACT_APP_BACKEND_URL: "http://backend-service:5000"
  NGINX_PORT: "80"
```

**Backend ConfigMap**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  NODE_ENV: "production"
  PORT: "5000"
  LOG_LEVEL: "info"
```

---

### 6. Secret Resource

**Purpose**: Stores sensitive data (passwords, API keys, tokens) with base64 encoding

**Attributes**:
- `metadata.name`: Secret identifier (e.g., "backend-secret")
- `metadata.namespace`: Kubernetes namespace
- `type`: Secret type (Opaque for generic secrets, kubernetes.io/tls for TLS certs)
- `data`: Key-value pairs with base64-encoded values
- `stringData`: Plain-text key-value pairs (auto-encoded to base64)

**Relationships**:
- **Referenced by**: Deployment/StatefulSet (as environment variables or mounted files)
- **Injected into**: Pods (at creation time)

**Validation Rules**:
- Values in `data` must be base64-encoded
- Keys must be valid environment variable names
- Total size limit: 1MiB per Secret
- Secrets are not encrypted at rest in etcd by default (Minikube limitation)

**Secret Example**:

**Backend Secret** (MongoDB connection):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secret
type: Opaque
stringData:
  MONGODB_URI: "mongodb://mongodb-service:27017/todos"
  API_KEY: "your-api-key-here"  # For AI chatbot service
```

**Security Notes**:
- Secrets are base64-encoded, NOT encrypted (anyone with cluster access can decode)
- For production, use external secret management (HashiCorp Vault, AWS Secrets Manager)
- Phase IV accepts Minikube's default secret handling

---

### 7. Ingress Resource

**Purpose**: Manages external HTTP/HTTPS access to services via routing rules

**Attributes**:
- `metadata.name`: Ingress identifier (e.g., "todo-app-ingress")
- `metadata.namespace`: Kubernetes namespace
- `metadata.annotations`: Ingress controller-specific configuration (e.g., `nginx.ingress.kubernetes.io/rewrite-target`)
- `spec.ingressClassName`: Ingress controller class ("nginx" for Minikube)
- `spec.rules`: HTTP routing rules (host, paths, backend service)
- `spec.tls`: TLS configuration (optional; out of scope for Phase IV)

**Relationships**:
- **Routes to**: Service (backend service for path-based routing)
- **Managed by**: Ingress Controller (Nginx in Minikube)
- **Requires**: DNS resolution (manual /etc/hosts entry for local development)

**Validation Rules**:
- At least one rule defined
- Each rule must reference an existing service
- Ingress controller addon must be enabled in Minikube (`minikube addons enable ingress`)
- Host-based routing requires DNS or /etc/hosts configuration

**Ingress Example**:

**Todo App Ingress** (path-based routing):
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: todo-app.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 5000
```

**DNS Configuration**:
```bash
# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
<minikube-ip> todo-app.local

# Get Minikube IP
minikube ip
```

---

### 8. Helm Release (Meta-Entity)

**Purpose**: Represents an installed instance of a Helm chart with versioned configuration

**Attributes**:
- `name`: Release name (e.g., "todo-frontend", "todo-backend", "todo-database")
- `namespace`: Target Kubernetes namespace
- `chart`: Chart name and version (e.g., "frontend-0.1.0")
- `values`: Merged values from values.yaml and --set overrides
- `revision`: Incremental revision number (1, 2, 3, ...; incremented on upgrade)
- `status`: deployed, failed, pending, uninstalling

**Relationships**:
- **Installs**: Multiple Kubernetes resources (Deployment, Service, ConfigMap, Secret, etc.)
- **Tracked by**: Helm (metadata stored as Secrets in namespace)
- **Versioned by**: Revision number (enables rollback)

**Validation Rules**:
- Release name must be unique within namespace
- Chart must pass `helm lint` validation
- All referenced images must be available (imagePullPolicy: IfNotPresent for local images)

**Helm Operations**:
- **Install**: `helm install <release-name> <chart-path> --values <values.yaml>`
- **Upgrade**: `helm upgrade <release-name> <chart-path> --values <values.yaml>`
- **Rollback**: `helm rollback <release-name> <revision>`
- **Uninstall**: `helm uninstall <release-name>`
- **Status**: `helm status <release-name>`

---

## Resource Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                         Minikube Cluster                        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Namespace: default                     │  │
│  │                                                           │  │
│  │  ┌─────────────────┐                                     │  │
│  │  │ Helm Release    │                                     │  │
│  │  │ "todo-frontend" │                                     │  │
│  │  └────────┬────────┘                                     │  │
│  │           │ installs                                     │  │
│  │           ├──> Deployment (frontend-deployment)         │  │
│  │           ├──> Service (frontend-service: NodePort)     │  │
│  │           └──> ConfigMap (frontend-config)              │  │
│  │                                                           │  │
│  │  ┌─────────────────┐                                     │  │
│  │  │ Helm Release    │                                     │  │
│  │  │ "todo-backend"  │                                     │  │
│  │  └────────┬────────┘                                     │  │
│  │           │ installs                                     │  │
│  │           ├──> Deployment (backend-deployment)          │  │
│  │           ├──> Service (backend-service: ClusterIP)     │  │
│  │           ├──> ConfigMap (backend-config)               │  │
│  │           └──> Secret (backend-secret)                  │  │
│  │                                                           │  │
│  │  ┌─────────────────┐                                     │  │
│  │  │ Helm Release    │                                     │  │
│  │  │ "todo-database" │                                     │  │
│  │  └────────┬────────┘                                     │  │
│  │           │ installs                                     │  │
│  │           ├──> StatefulSet (mongodb)                    │  │
│  │           ├──> Service (mongodb-service: ClusterIP)     │  │
│  │           └──> PVC (data-mongodb-0)                     │  │
│  │                                                           │  │
│  │  ┌─────────────────┐                                     │  │
│  │  │ Ingress         │                                     │  │
│  │  │ "todo-app-ingress" (optional)                        │  │
│  │  └─────────────────┘                                     │  │
│  │        Routes HTTP → frontend-service & backend-service  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Dependency Order** (installation sequence):

1. **Database Layer**: Install `todo-database` release first (backend depends on it)
2. **Backend Layer**: Install `todo-backend` release (frontend depends on it)
3. **Frontend Layer**: Install `todo-frontend` release (user-facing; depends on backend)
4. **Ingress Layer** (optional): Install Ingress resource after all services are running

---

## Helm Chart Values Schema

### Frontend Chart Values (charts/frontend/values.yaml)

```yaml
# Replica configuration
replicaCount: 2

# Container image
image:
  repository: todo-frontend
  tag: 1.0.0
  pullPolicy: IfNotPresent

# Service configuration
service:
  type: NodePort  # or ClusterIP if using Ingress
  port: 80
  nodePort: 30080  # Fixed NodePort for consistency (optional)

# Resource limits
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi

# Environment configuration (ConfigMap)
config:
  backendUrl: "http://backend-service:5000"
  nginxPort: "80"

# Health probes
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

### Backend Chart Values (charts/backend/values.yaml)

```yaml
# Replica configuration
replicaCount: 1

# Container image
image:
  repository: todo-backend
  tag: 1.0.0
  pullPolicy: IfNotPresent

# Service configuration
service:
  type: ClusterIP
  port: 5000

# Resource limits
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi

# Environment configuration (ConfigMap)
config:
  nodeEnv: "production"
  port: "5000"
  logLevel: "info"

# Secrets (sensitive data)
secret:
  mongodbUri: "mongodb://mongodb-service:27017/todos"
  apiKey: "your-ai-api-key-here"

# Health probes
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 15
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 5
```

### Database Chart Values (charts/database/values.yaml)

```yaml
# Replica configuration (single instance for Phase IV)
replicaCount: 1

# Container image
image:
  repository: mongo
  tag: "7"
  pullPolicy: IfNotPresent

# Service configuration
service:
  type: ClusterIP
  port: 27017

# Persistence
persistence:
  enabled: true
  storageClass: "standard"  # Minikube default
  accessMode: ReadWriteOnce
  size: 5Gi

# Resource limits
resources:
  requests:
    cpu: 250m
    memory: 512Mi
  limits:
    cpu: 500m
    memory: 1Gi

# MongoDB configuration
mongodbDatabase: "todos"
mongodbRootUsername: "admin"  # For authentication (Phase IV: optional)
mongodbRootPassword: "changeme"  # Stored in Secret
```

---

## Entity Relationships Summary

| Parent Entity | Child Entity | Relationship | Cardinality |
|---------------|--------------|--------------|-------------|
| Helm Release | Deployment | Installs | 1 → 1+ |
| Helm Release | Service | Installs | 1 → 1+ |
| Helm Release | ConfigMap | Installs | 1 → 0+ |
| Helm Release | Secret | Installs | 1 → 0+ |
| Helm Release | StatefulSet | Installs | 1 → 0-1 |
| Deployment | ReplicaSet | Manages | 1 → 1+ |
| Deployment | Pod | Creates (via ReplicaSet) | 1 → N |
| StatefulSet | Pod | Creates | 1 → N (ordinal) |
| StatefulSet | PVC | Creates (via volumeClaimTemplates) | 1 → N |
| Service | Pod | Targets (via selector) | 1 → N |
| Ingress | Service | Routes to | 1 → N |
| ConfigMap | Pod | Injected into | 1 → N |
| Secret | Pod | Injected into | 1 → N |
| PVC | PV | Bound to | 1 → 1 |
| PV | StorageClass | Provisioned by | 1 → 1 |

---

## Validation & Constraints

**Constitution Compliance**:
- ✅ **Independent Containerization** (Principle V): Frontend and Backend have separate Deployments, Services, ConfigMaps
- ✅ **Cloud-Native Best Practices** (Principle II): Health probes, resource limits, Secrets, ConfigMaps defined
- ✅ **Helm Over Raw Manifests** (Principle IV): All resources templated in Helm charts
- ✅ **Local-First Deployment** (Principle III): StorageClass=standard (Minikube hostPath), no cloud-specific resources

**Kubernetes API Version Compatibility**:
- Deployment: `apps/v1` (Kubernetes 1.28+)
- Service: `v1` (stable API)
- StatefulSet: `apps/v1` (Kubernetes 1.28+)
- Ingress: `networking.k8s.io/v1` (Kubernetes 1.19+)
- ConfigMap, Secret: `v1` (stable API)

**Resource Naming Conventions**:
- Use lowercase alphanumeric + hyphens (RFC 1123)
- Prefix with chart name (e.g., `frontend-deployment`, `backend-service`)
- Max length: 253 characters
- Labels: Use `app`, `tier`, `release` keys for consistency

---

**Data Model Completed By**: Claude Sonnet 4.5 (Orchestrator Agent)
**Date**: 2026-01-07
**Next Phase**: Generate API contracts (Helm chart templates and values.yaml schemas)
