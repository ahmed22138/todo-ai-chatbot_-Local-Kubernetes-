# Helm Charts Specification

**Feature**: Cloud-Native Kubernetes Deployment
**Branch**: `1-k8s-deployment`
**Date**: 2026-01-07
**Status**: Complete

## Purpose

This document specifies the Helm chart structure, templates, and configuration contracts for the three microservices: Frontend, Backend, and Database. Each chart is independently installable and follows Helm best practices.

---

## Chart Directory Structure

```
charts/
├── frontend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   ├── _helpers.tpl
│   │   └── NOTES.txt
│   └── README.md
│
├── backend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── _helpers.tpl
│   │   └── NOTES.txt
│   └── README.md
│
└── database/
    ├── Chart.yaml
    ├── values.yaml
    ├── templates/
    │   ├── statefulset.yaml
    │   ├── service.yaml
    │   ├── pvc.yaml (if not using volumeClaimTemplates)
    │   ├── _helpers.tpl
    │   └── NOTES.txt
    └── README.md
```

---

## Chart Metadata (Chart.yaml)

### Frontend Chart Metadata

```yaml
apiVersion: v2
name: frontend
description: Todo AI Chatbot Frontend - React application served by Nginx
type: application
version: 0.1.0  # Chart version (MAJOR.MINOR.PATCH)
appVersion: "1.0.0"  # Application version (Docker image tag)
keywords:
  - frontend
  - react
  - nginx
  - todo-app
maintainers:
  - name: Phase IV Team
    email: phase4@example.com
sources:
  - https://github.com/your-org/todo-app
```

### Backend Chart Metadata

```yaml
apiVersion: v2
name: backend
description: Todo AI Chatbot Backend - Node.js API server
type: application
version: 0.1.0
appVersion: "1.0.0"
keywords:
  - backend
  - nodejs
  - api
  - todo-app
maintainers:
  - name: Phase IV Team
    email: phase4@example.com
sources:
  - https://github.com/your-org/todo-app
```

### Database Chart Metadata

```yaml
apiVersion: v2
name: database
description: MongoDB database for Todo AI Chatbot
type: application
version: 0.1.0
appVersion: "7"  # MongoDB version
keywords:
  - database
  - mongodb
  - statefulset
maintainers:
  - name: Phase IV Team
    email: phase4@example.com
sources:
  - https://hub.docker.com/_/mongo
```

---

## Helm Template Contracts

### Frontend Chart Templates

#### 1. deployment.yaml Template Contract

**Purpose**: Deploys React frontend as Deployment with 2 replicas (configurable)

**Template Variables**:
- `{{ .Values.replicaCount }}`: Number of replicas (default: 2)
- `{{ .Values.image.repository }}`: Image name (default: "todo-frontend")
- `{{ .Values.image.tag }}`: Image tag (default: "1.0.0")
- `{{ .Values.image.pullPolicy }}`: Pull policy (default: "IfNotPresent")
- `{{ .Values.resources }}`: Resource requests/limits
- `{{ .Values.livenessProbe }}`: Liveness probe configuration
- `{{ .Values.readinessProbe }}`: Readiness probe configuration

**Required Labels**:
- `app.kubernetes.io/name: {{ include "frontend.name" . }}`
- `app.kubernetes.io/instance: {{ .Release.Name }}`
- `app.kubernetes.io/version: {{ .Chart.AppVersion }}`

**Required Annotations**:
- `checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}`
  (Forces pod restart on ConfigMap change)

**Template Output** (condensed):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "frontend.fullname" . }}
  labels:
    {{- include "frontend.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "frontend.selectorLabels" . | nindent 6 }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      labels:
        {{- include "frontend.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 80
          protocol: TCP
        livenessProbe:
          {{- toYaml .Values.livenessProbe | nindent 10 }}
        readinessProbe:
          {{- toYaml .Values.readinessProbe | nindent 10 }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
        envFrom:
        - configMapRef:
            name: {{ include "frontend.fullname" . }}-config
```

#### 2. service.yaml Template Contract

**Purpose**: Exposes frontend via NodePort or ClusterIP (for Ingress)

**Template Variables**:
- `{{ .Values.service.type }}`: Service type (default: "NodePort")
- `{{ .Values.service.port }}`: Service port (default: 80)
- `{{ .Values.service.nodePort }}`: NodePort (default: auto-assigned)

**Template Output**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "frontend.fullname" . }}-service
  labels:
    {{- include "frontend.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
  - port: {{ .Values.service.port }}
    targetPort: http
    protocol: TCP
    name: http
    {{- if and (eq .Values.service.type "NodePort") .Values.service.nodePort }}
    nodePort: {{ .Values.service.nodePort }}
    {{- end }}
  selector:
    {{- include "frontend.selectorLabels" . | nindent 4 }}
```

#### 3. configmap.yaml Template Contract

**Purpose**: Provides environment variables for frontend container

**Template Variables**:
- `{{ .Values.config.backendUrl }}`: Backend API URL (default: "http://backend-service:5000")
- `{{ .Values.config.nginxPort }}`: Nginx port (default: "80")

**Template Output**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "frontend.fullname" . }}-config
  labels:
    {{- include "frontend.labels" . | nindent 4 }}
data:
  REACT_APP_BACKEND_URL: {{ .Values.config.backendUrl | quote }}
  NGINX_PORT: {{ .Values.config.nginxPort | quote }}
```

---

### Backend Chart Templates

#### 1. deployment.yaml Template Contract

**Purpose**: Deploys Node.js backend as Deployment with 1 replica (configurable)

**Template Variables**:
- `{{ .Values.replicaCount }}`: Number of replicas (default: 1)
- `{{ .Values.image.repository }}`: Image name (default: "todo-backend")
- `{{ .Values.image.tag }}`: Image tag (default: "1.0.0")
- `{{ .Values.resources }}`: Resource requests/limits
- `{{ .Values.livenessProbe }}`: Liveness probe configuration (GET /health)
- `{{ .Values.readinessProbe }}`: Readiness probe configuration (GET /ready)

**Required Labels**: Same pattern as frontend

**Required Annotations**:
- `checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}`
- `checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}`

**Template Output** (condensed):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "backend.fullname" . }}
  labels:
    {{- include "backend.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "backend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
      labels:
        {{- include "backend.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 5000
          protocol: TCP
        livenessProbe:
          {{- toYaml .Values.livenessProbe | nindent 10 }}
        readinessProbe:
          {{- toYaml .Values.readinessProbe | nindent 10 }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
        envFrom:
        - configMapRef:
            name: {{ include "backend.fullname" . }}-config
        - secretRef:
            name: {{ include "backend.fullname" . }}-secret
```

#### 2. service.yaml Template Contract

**Purpose**: Exposes backend via ClusterIP (internal only)

**Template Variables**:
- `{{ .Values.service.type }}`: Service type (default: "ClusterIP")
- `{{ .Values.service.port }}`: Service port (default: 5000)

**Template Output**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "backend.fullname" . }}-service
  labels:
    {{- include "backend.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
  - port: {{ .Values.service.port }}
    targetPort: http
    protocol: TCP
    name: http
  selector:
    {{- include "backend.selectorLabels" . | nindent 4 }}
```

#### 3. configmap.yaml Template Contract

**Purpose**: Provides non-sensitive environment variables for backend

**Template Variables**:
- `{{ .Values.config.nodeEnv }}`: Node environment (default: "production")
- `{{ .Values.config.port }}`: Server port (default: "5000")
- `{{ .Values.config.logLevel }}`: Log level (default: "info")

**Template Output**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "backend.fullname" . }}-config
  labels:
    {{- include "backend.labels" . | nindent 4 }}
data:
  NODE_ENV: {{ .Values.config.nodeEnv | quote }}
  PORT: {{ .Values.config.port | quote }}
  LOG_LEVEL: {{ .Values.config.logLevel | quote }}
```

#### 4. secret.yaml Template Contract

**Purpose**: Provides sensitive environment variables for backend

**Template Variables**:
- `{{ .Values.secret.mongodbUri }}`: MongoDB connection string (default: "mongodb://mongodb-service:27017/todos")
- `{{ .Values.secret.apiKey }}`: AI chatbot API key (default: placeholder)

**Template Output**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "backend.fullname" . }}-secret
  labels:
    {{- include "backend.labels" . | nindent 4 }}
type: Opaque
stringData:
  MONGODB_URI: {{ .Values.secret.mongodbUri | quote }}
  API_KEY: {{ .Values.secret.apiKey | quote }}
```

---

### Database Chart Templates

#### 1. statefulset.yaml Template Contract

**Purpose**: Deploys MongoDB as StatefulSet with persistent storage

**Template Variables**:
- `{{ .Values.replicaCount }}`: Number of replicas (default: 1)
- `{{ .Values.image.repository }}`: Image name (default: "mongo")
- `{{ .Values.image.tag }}`: Image tag (default: "7")
- `{{ .Values.persistence.enabled }}`: Enable PVC (default: true)
- `{{ .Values.persistence.storageClass }}`: StorageClass (default: "standard")
- `{{ .Values.persistence.size }}`: Storage size (default: "5Gi")

**Template Output** (condensed):
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {{ include "database.fullname" . }}
  labels:
    {{- include "database.labels" . | nindent 4 }}
spec:
  serviceName: {{ include "database.fullname" . }}-service
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "database.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "database.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: mongodb
          containerPort: 27017
          protocol: TCP
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
        volumeMounts:
        - name: data
          mountPath: /data/db
  {{- if .Values.persistence.enabled }}
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: {{ .Values.persistence.storageClass }}
      resources:
        requests:
          storage: {{ .Values.persistence.size }}
  {{- end }}
```

#### 2. service.yaml Template Contract

**Purpose**: Exposes MongoDB via ClusterIP (internal only)

**Template Variables**:
- `{{ .Values.service.type }}`: Service type (default: "ClusterIP")
- `{{ .Values.service.port }}`: Service port (default: 27017)

**Template Output**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "database.fullname" . }}-service
  labels:
    {{- include "database.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
  - port: {{ .Values.service.port }}
    targetPort: mongodb
    protocol: TCP
    name: mongodb
  selector:
    {{- include "database.selectorLabels" . | nindent 4 }}
```

---

## Helm Helper Templates (_helpers.tpl)

### Common Helpers (used in all charts)

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "CHARTNAME.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "CHARTNAME.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "CHARTNAME.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "CHARTNAME.labels" -}}
helm.sh/chart: {{ include "CHARTNAME.chart" . }}
{{ include "CHARTNAME.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "CHARTNAME.selectorLabels" -}}
app.kubernetes.io/name: {{ include "CHARTNAME.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

Replace `CHARTNAME` with `frontend`, `backend`, or `database` in each chart's `_helpers.tpl`.

---

## NOTES.txt Templates

### Frontend NOTES.txt

```text
🎉 Frontend deployed successfully!

Your release is named {{ .Release.Name }}.

To access the frontend application:

{{- if eq .Values.service.type "NodePort" }}
1. Get the application URL:

   export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ include "frontend.fullname" . }}-service)
   export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
   echo http://$NODE_IP:$NODE_PORT

2. Open the URL in your browser.

{{- else if eq .Values.service.type "ClusterIP" }}
1. Forward the port:

   kubectl port-forward --namespace {{ .Release.Namespace }} svc/{{ include "frontend.fullname" . }}-service 8080:{{ .Values.service.port }}

2. Access at: http://localhost:8080

{{- end }}

To check pod status:
  kubectl get pods --namespace {{ .Release.Namespace }} -l "app.kubernetes.io/name={{ include "frontend.name" . }},app.kubernetes.io/instance={{ .Release.Name }}"

To view logs:
  kubectl logs --namespace {{ .Release.Namespace }} -l "app.kubernetes.io/name={{ include "frontend.name" . }}" --tail=50
```

### Backend NOTES.txt

```text
✅ Backend deployed successfully!

Your release is named {{ .Release.Name }}.

The backend is accessible internally at:
  http://{{ include "backend.fullname" . }}-service:{{ .Values.service.port }}

To test the backend from within the cluster:

1. Run a debug pod:

   kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
     curl http://{{ include "backend.fullname" . }}-service:{{ .Values.service.port }}/health

2. Check backend health:
   - Liveness: /health
   - Readiness: /ready

To check pod status:
  kubectl get pods --namespace {{ .Release.Namespace }} -l "app.kubernetes.io/name={{ include "backend.name" . }},app.kubernetes.io/instance={{ .Release.Name }}"

To view logs:
  kubectl logs --namespace {{ .Release.Namespace }} -l "app.kubernetes.io/name={{ include "backend.name" . }}" --tail=50 -f
```

### Database NOTES.txt

```text
💾 Database deployed successfully!

Your release is named {{ .Release.Name }}.

MongoDB is accessible internally at:
  mongodb://{{ include "database.fullname" . }}-service:{{ .Values.service.port }}/todos

To connect to MongoDB from within the cluster:

1. Run a MongoDB client pod:

   kubectl run -it --rm mongo-client --image=mongo:7 --restart=Never -- \
     mongosh mongodb://{{ include "database.fullname" . }}-service:{{ .Values.service.port }}/todos

2. Check database status:

   kubectl exec -it {{ include "database.fullname" . }}-0 -- mongosh --eval "db.adminCommand('ping')"

To check StatefulSet status:
  kubectl get statefulset --namespace {{ .Release.Namespace }} {{ include "database.fullname" . }}

To check PVC status:
  kubectl get pvc --namespace {{ .Release.Namespace }}

⚠️  Warning: Data persists in PVC even after helm uninstall. To delete data:
  kubectl delete pvc data-{{ include "database.fullname" . }}-0 --namespace {{ .Release.Namespace }}
```

---

## Helm Chart Validation

### Linting Commands

```bash
# Lint each chart
helm lint charts/frontend
helm lint charts/backend
helm lint charts/database

# Validate template rendering
helm template frontend charts/frontend
helm template backend charts/backend
helm template database charts/database

# Dry-run install
helm install --dry-run --debug frontend charts/frontend
helm install --dry-run --debug backend charts/backend
helm install --dry-run --debug database charts/database
```

### Expected Lint Results

- ✅ No errors
- ⚠️ Warnings acceptable: missing icon, missing home URL (optional metadata)
- ❌ Errors must be fixed: invalid YAML, missing required fields, template syntax errors

---

## Installation Commands

### Order of Installation

```bash
# 1. Database first (backend depends on it)
helm install todo-database charts/database

# 2. Backend (frontend depends on it)
helm install todo-backend charts/backend

# 3. Frontend (user-facing)
helm install todo-frontend charts/frontend

# 4. Verify all releases
helm list
```

### Installation with Custom Values

```bash
# Override default values
helm install todo-frontend charts/frontend \
  --set replicaCount=3 \
  --set image.tag=1.0.1 \
  --set service.type=ClusterIP

# Use custom values file
helm install todo-backend charts/backend \
  --values custom-values.yaml
```

---

## Agent Responsibilities

| Artifact | Responsible Agent | Inputs | Outputs |
|----------|------------------|--------|---------|
| Chart.yaml | Claude Sonnet 4.5 | Chart metadata from research.md | Chart.yaml files |
| values.yaml | Claude Sonnet 4.5 | Default configs from data-model.md | values.yaml files |
| Templates (deployment.yaml, service.yaml, etc.) | Claude Sonnet 4.5 + kubectl-ai | Kubernetes best practices | Template YAML files |
| _helpers.tpl | Claude Sonnet 4.5 | Helm templating patterns | Helper functions |
| NOTES.txt | Claude Sonnet 4.5 | User guidance from spec.md | Post-install instructions |
| Validation | kubectl-ai, kagent | Rendered templates | Lint results, best-practice audit |

**No manual coding**: All chart artifacts generated by AI agents per Constitution Principle I.

---

**Contracts Completed By**: Claude Sonnet 4.5 (Orchestrator Agent)
**Date**: 2026-01-07
**Next Phase**: Generate quickstart.md deployment guide
