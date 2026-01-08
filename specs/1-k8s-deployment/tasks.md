# Tasks: Cloud-Native Kubernetes Deployment

**Input**: Design documents from `/specs/1-k8s-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Post-deployment smoke tests included (scripts/validate-deployment.sh)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/`, `backend/`, `charts/`, `scripts/` at repository root
- Helm charts: `charts/frontend/`, `charts/backend/`, `charts/database/`
- Scripts: `scripts/check-prerequisites.sh`, `scripts/validate-deployment.sh`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and prerequisite verification

- [x] T001 Create scripts directory for deployment automation scripts
- [x] T002 [P] Create charts directory for Helm chart storage
- [x] T003 [P] Verify Docker Desktop is installed and running (docker --version)
- [x] T004 [P] Verify Minikube is installed (minikube version)
- [x] T005 [P] Verify kubectl is installed (kubectl version --client)
- [x] T006 [P] Verify Helm is installed (helm version)

**Checkpoint**: Prerequisites verified - ready for cluster setup

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Minikube cluster must be operational before ANY deployment can occur

**⚠️ CRITICAL**: No deployment work can begin until this phase is complete

### User Story 1 (P1): Local Cluster Setup and Validation

**Goal**: Initialize and validate a functional Minikube Kubernetes cluster

**Independent Test**: Run `minikube start` and validate cluster health with `kubectl cluster-info` and `kubectl get nodes`. Success means cluster status "Ready" with ingress and metrics-server addons enabled.

- [ ] T007 [US1] Start Minikube cluster with recommended resources: `minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker`
- [ ] T008 [US1] Wait for Minikube cluster to be ready: `kubectl cluster-info`
- [ ] T009 [US1] Verify cluster nodes are ready: `kubectl get nodes` (status should be "Ready")
- [ ] T010 [P] [US1] Enable Nginx Ingress Controller addon: `minikube addons enable ingress`
- [ ] T011 [P] [US1] Enable Metrics Server addon: `minikube addons enable metrics-server`
- [ ] T012 [US1] Verify ingress controller pods are running: `kubectl get pods -n ingress-nginx`
- [ ] T013 [US1] Verify metrics-server pods are running: `kubectl get pods -n kube-system -l k8s-app=metrics-server`
- [ ] T014 [US1] Generate prerequisite validation script in scripts/check-prerequisites.sh using Claude
- [ ] T015 [US1] Execute prerequisite validation script: `bash scripts/check-prerequisites.sh` (should pass all checks)
- [ ] T016 [US1] **[OPTIONAL - if kagent available]** Run cluster health analysis: `kagent analyze cluster`

**Checkpoint**: Minikube cluster fully operational with addons enabled - ready for service deployment

---

## Phase 3: User Story 2 (P2) - Backend Service Deployment 🎯 First Deployable Service

**Goal**: Deploy Backend API service with database dependency, health checks, and internal service access

**Independent Test**: Deploy backend Helm chart, verify pods running, health checks passing, and internal DNS resolution working via `kubectl exec` testing

### Backend Dockerfile & Image

- [ ] T017 [P] [US2] Generate frontend/.dockerignore excluding node_modules, .git, .env using Claude
- [ ] T018 [P] [US2] Generate backend/.dockerignore excluding node_modules, .git, .env using Claude
- [ ] T019 [P] [US2] **[AI-GENERATED]** Generate backend/Dockerfile using Gordon (Docker AI Agent) with multi-stage build (Node.js 18 builder + runtime), health check on /health endpoint
- [ ] T020 [P] [US2] **[AI-GENERATED - if Gordon unavailable]** Generate backend/Dockerfile using Claude following Gordon's patterns (multi-stage, Alpine, non-root user, health check)
- [ ] T021 [US2] Build backend Docker image: `docker build -t todo-backend:1.0.0 ./backend`
- [ ] T022 [US2] Verify backend image built successfully: `docker images | grep todo-backend` (size should be < 100MB)
- [ ] T023 [US2] Load backend image into Minikube: `minikube image load todo-backend:1.0.0`
- [ ] T024 [US2] Verify backend image available in Minikube: `minikube image ls | grep todo-backend`

### Database Helm Chart & Deployment

- [ ] T025 [P] [US2] **[AI-GENERATED]** Generate charts/database/Chart.yaml with metadata (name: database, version: 0.1.0, appVersion: "7") using Claude
- [ ] T026 [P] [US2] **[AI-GENERATED]** Generate charts/database/values.yaml with MongoDB configuration (image: mongo:7, persistence: 5Gi, storageClass: standard) using Claude
- [ ] T027 [P] [US2] **[AI-GENERATED]** Generate charts/database/templates/_helpers.tpl with template functions for labels and selectors using Claude
- [ ] T028 [P] [US2] **[AI-GENERATED]** Generate charts/database/templates/statefulset.yaml with MongoDB StatefulSet, volumeClaimTemplates, resource limits using Claude
- [ ] T029 [P] [US2] **[AI-GENERATED]** Generate charts/database/templates/service.yaml with ClusterIP service on port 27017 using Claude
- [ ] T030 [P] [US2] **[AI-GENERATED]** Generate charts/database/templates/NOTES.txt with post-install connection instructions using Claude
- [ ] T031 [P] [US2] **[AI-GENERATED]** Generate charts/database/README.md documenting chart parameters and usage using Claude
- [ ] T032 [US2] Lint database Helm chart: `helm lint charts/database` (should pass with no errors)
- [ ] T033 [US2] Dry-run database chart installation: `helm install --dry-run --debug todo-database charts/database` (should render valid YAML)
- [ ] T034 [US2] Install database Helm chart: `helm install todo-database charts/database`
- [ ] T035 [US2] Wait for database pod to be ready: `kubectl wait --for=condition=ready pod/todo-database-0 --timeout=120s`
- [ ] T036 [US2] Verify database StatefulSet created: `kubectl get statefulset todo-database`
- [ ] T037 [US2] Verify database PVC created and bound: `kubectl get pvc` (status should be "Bound")
- [ ] T038 [US2] Test database connectivity from debug pod: `kubectl run -it --rm mongo-test --image=mongo:7 --restart=Never -- mongosh mongodb://todo-database-service:27017/todos --eval "db.adminCommand('ping')"`

### Backend Helm Chart & Deployment

- [ ] T039 [P] [US2] **[AI-GENERATED]** Generate charts/backend/Chart.yaml with metadata (name: backend, version: 0.1.0, appVersion: "1.0.0") using Claude
- [ ] T040 [P] [US2] **[AI-GENERATED]** Generate charts/backend/values.yaml with backend configuration (image: todo-backend:1.0.0, replicas: 1, resources, probes) using Claude
- [ ] T041 [P] [US2] **[AI-GENERATED]** Generate charts/backend/templates/_helpers.tpl with template functions for labels and selectors using Claude
- [ ] T042 [P] [US2] **[AI-GENERATED]** Generate charts/backend/templates/deployment.yaml with Deployment, health probes (/health, /ready), resource limits, env from ConfigMap/Secret using Claude
- [ ] T043 [P] [US2] **[AI-GENERATED]** Generate charts/backend/templates/service.yaml with ClusterIP service on port 5000 using Claude
- [ ] T044 [P] [US2] **[AI-GENERATED]** Generate charts/backend/templates/configmap.yaml with NODE_ENV, PORT, LOG_LEVEL environment variables using Claude
- [ ] T045 [P] [US2] **[AI-GENERATED]** Generate charts/backend/templates/secret.yaml with MONGODB_URI (mongodb://todo-database-service:27017/todos) and API_KEY using Claude
- [ ] T046 [P] [US2] **[AI-GENERATED]** Generate charts/backend/templates/NOTES.txt with post-install health check instructions using Claude
- [ ] T047 [P] [US2] **[AI-GENERATED]** Generate charts/backend/README.md documenting chart parameters and usage using Claude
- [ ] T048 [US2] Lint backend Helm chart: `helm lint charts/backend` (should pass with no errors)
- [ ] T049 [US2] Dry-run backend chart installation: `helm install --dry-run --debug todo-backend charts/backend` (should render valid YAML)
- [ ] T050 [US2] Install backend Helm chart: `helm install todo-backend charts/backend`
- [ ] T051 [US2] Wait for backend pod to be ready: `kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=backend --timeout=120s`
- [ ] T052 [US2] Verify backend Deployment created: `kubectl get deployment todo-backend-deployment`
- [ ] T053 [US2] Verify backend pod count is 1: `kubectl get pods -l app.kubernetes.io/name=backend` (should show 1/1 Running)
- [ ] T054 [US2] Verify backend service endpoints: `kubectl get endpoints todo-backend-service` (should have pod IPs)
- [ ] T055 [US2] Test backend health endpoint from debug pod: `kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl -f http://todo-backend-service:5000/health`
- [ ] T056 [US2] Test backend readiness endpoint from debug pod: `kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl -f http://todo-backend-service:5000/ready`
- [ ] T057 [US2] Check backend logs for startup errors: `kubectl logs -l app.kubernetes.io/name=backend --tail=50`
- [ ] T058 [US2] **[OPTIONAL - if kagent available]** Analyze backend deployment best practices: `kagent analyze deployment todo-backend-deployment`

**Checkpoint**: Backend service fully deployed and healthy - ready for frontend deployment

---

## Phase 4: User Story 3 (P3) - Frontend Service Deployment

**Goal**: Deploy Frontend application, expose externally, and validate communication with backend

**Independent Test**: Deploy frontend Helm chart, access via NodePort/Ingress URL, verify UI loads and communicates with backend API

### Frontend Dockerfile & Image

- [x] T059 [P] [US3] **[AI-GENERATED]** Generate frontend/Dockerfile using Gordon (Docker AI Agent) with multi-stage build (Node.js 18 builder + Nginx runtime), custom nginx.conf for SPA routing
- [x] T060 [P] [US3] **[AI-GENERATED - if Gordon unavailable]** Generate frontend/Dockerfile using Claude following Gordon's patterns (multi-stage, Alpine, Nginx, non-root user)
- [x] T061 [P] [US3] **[AI-GENERATED]** Generate frontend/nginx.conf for SPA routing (try_files $uri /index.html) using Claude
- [x] T062 [US3] Build frontend Docker image: `docker build -t todo-frontend:1.0.0 ./frontend`
- [x] T063 [US3] Verify frontend image built successfully: `docker images | grep todo-frontend` (size should be < 50MB)
- [x] T064 [US3] Load frontend image into Minikube: `minikube image load todo-frontend:1.0.0`
- [x] T065 [US3] Verify frontend image available in Minikube: `minikube image ls | grep todo-frontend`

### Frontend Helm Chart & Deployment

- [x] T066 [P] [US3] **[AI-GENERATED]** Generate charts/frontend/Chart.yaml with metadata (name: frontend, version: 0.1.0, appVersion: "1.0.0") using Claude
- [x] T067 [P] [US3] **[AI-GENERATED]** Generate charts/frontend/values.yaml with frontend configuration (image: todo-frontend:1.0.0, replicas: 2, resources, probes, service type: NodePort) using Claude
- [x] T068 [P] [US3] **[AI-GENERATED]** Generate charts/frontend/templates/_helpers.tpl with template functions for labels and selectors using Claude
- [x] T069 [P] [US3] **[AI-GENERATED]** Generate charts/frontend/templates/deployment.yaml with Deployment, health probes (GET /), resource limits, env from ConfigMap using Claude
- [x] T070 [P] [US3] **[AI-GENERATED]** Generate charts/frontend/templates/service.yaml with NodePort service on port 80 using Claude
- [x] T071 [P] [US3] **[AI-GENERATED]** Generate charts/frontend/templates/configmap.yaml with REACT_APP_BACKEND_URL (http://todo-backend-service:5000) using Claude
- [x] T072 [P] [US3] **[AI-GENERATED]** Generate charts/frontend/templates/NOTES.txt with post-install access instructions (minikube service command) using Claude
- [x] T073 [P] [US3] **[AI-GENERATED]** Generate charts/frontend/README.md documenting chart parameters and usage using Claude
- [x] T074 [US3] Lint frontend Helm chart: `helm lint charts/frontend` (should pass with no errors)
- [x] T075 [US3] Dry-run frontend chart installation: `helm install --dry-run --debug todo-frontend charts/frontend` (should render valid YAML)
- [x] T076 [US3] Install frontend Helm chart: `helm install todo-frontend charts/frontend`
- [x] T077 [US3] Wait for frontend pods to be ready: `kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=frontend --timeout=120s`
- [x] T078 [US3] Verify frontend Deployment created: `kubectl get deployment todo-frontend-deployment`
- [x] T079 [US3] Verify frontend pod count is 2: `kubectl get pods -l app.kubernetes.io/name=frontend` (should show 2 pods with 1/1 Running)
- [x] T080 [US3] Verify frontend service created: `kubectl get service todo-frontend-service`
- [x] T081 [US3] Get frontend NodePort URL: `minikube service todo-frontend-service --url` (save URL for browser access)
- [x] T082 [US3] Test frontend accessibility via curl: `curl -f $(minikube service todo-frontend-service --url)` (should return HTML)
- [x] T083 [US3] Verify frontend can reach backend internally: Check browser network tab or frontend logs
- [x] T084 [US3] Check frontend logs for startup errors: `kubectl logs -l app.kubernetes.io/name=frontend --tail=50`
- [x] T085 [US3] **[OPTIONAL - if kagent available]** Analyze frontend deployment best practices: `kagent analyze deployment todo-frontend-deployment`

**Checkpoint**: Frontend accessible via browser and communicating with backend - core system operational

---

## Phase 5: User Story 4 (P4) - End-to-End System Validation

**Goal**: Validate complete system with automated smoke tests and manual UI testing

**Independent Test**: Run automated smoke tests (7 checks) and perform manual CRUD operations through frontend UI

### Smoke Test Script Generation & Execution

- [ ] T086 [P] [US4] **[AI-GENERATED]** Generate scripts/validate-deployment.sh with 7 smoke tests (cluster info, pods ready, frontend accessible, backend health, database connectivity, CRUD operations, resource utilization) using Claude
- [ ] T087 [US4] Make validation script executable: `chmod +x scripts/validate-deployment.sh`
- [ ] T088 [US4] Execute smoke test validation: `bash scripts/validate-deployment.sh` (all 7 tests should pass)

### Manual End-to-End Testing

- [ ] T089 [US4] Open frontend in browser using URL from T081
- [ ] T090 [US4] Create a new todo item via frontend UI (title: "Test Deployment", completed: false)
- [ ] T091 [US4] Verify todo item appears in UI list
- [ ] T092 [US4] Update todo item to completed status via UI
- [ ] T093 [US4] Delete todo item via UI
- [ ] T094 [US4] Verify data persistence by refreshing browser (todos should persist)
- [ ] T095 [US4] **[OPTIONAL - if AI chatbot feature exists]** Test AI chatbot interaction via UI

### Resource Monitoring & Health Analysis

- [ ] T096 [P] [US4] Check node resource utilization: `kubectl top nodes` (CPU and memory usage)
- [ ] T097 [P] [US4] Check pod resource utilization: `kubectl top pods` (identify high-usage pods)
- [ ] T098 [P] [US4] Verify all pods have passing health probes: `kubectl get pods --all-namespaces` (all should show READY status)
- [ ] T099 [US4] **[OPTIONAL - if kagent available]** Run comprehensive cluster analysis: `kagent analyze resources` (review resource utilization and rightsizing recommendations)
- [ ] T100 [US4] **[OPTIONAL - if kagent available]** Run security audit: `kagent audit security` (check for missing resource limits, privileged containers, exposed secrets)

### API Testing (Backend Validation)

- [ ] T101 [US4] Port-forward backend service for API testing: `kubectl port-forward svc/todo-backend-service 5000:5000 &`
- [ ] T102 [US4] Test API - Create todo: `curl -X POST http://localhost:5000/todos -H "Content-Type: application/json" -d '{"title":"API Test","completed":false}'`
- [ ] T103 [US4] Test API - Get all todos: `curl http://localhost:5000/todos` (should return JSON array with created todo)
- [ ] T104 [US4] Test API - Update todo: `curl -X PATCH http://localhost:5000/todos/<id> -H "Content-Type: application/json" -d '{"completed":true}'`
- [ ] T105 [US4] Test API - Delete todo: `curl -X DELETE http://localhost:5000/todos/<id>`
- [ ] T106 [US4] Stop port-forward process: `kill` the background port-forward process

**Checkpoint**: All smoke tests passing, manual UI/API testing successful, system fully validated

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup scripts, and operational improvements

### Documentation

- [ ] T107 [P] Update README.md with deployment overview and prerequisites
- [ ] T108 [P] Update README.md with quickstart commands (minikube start, helm install order)
- [ ] T109 [P] Update README.md with validation commands (smoke tests, health checks)
- [ ] T110 [P] Update README.md with troubleshooting section (common issues and solutions)
- [ ] T111 [P] Update README.md with cleanup commands (helm uninstall, PVC deletion, minikube stop/delete)

### Cleanup & Operational Scripts

- [ ] T112 [P] **[AI-GENERATED]** Generate scripts/cleanup-deployment.sh for uninstalling all Helm releases and deleting PVCs using Claude
- [ ] T113 [P] **[AI-GENERATED]** Generate scripts/upgrade-deployment.sh for upgrading Helm releases with new image tags using Claude
- [ ] T114 [P] **[AI-GENERATED]** Generate scripts/rollback-deployment.sh for rolling back Helm releases to previous revisions using Claude

### Optional Ingress Configuration

- [ ] T115 **[OPTIONAL]** **[AI-GENERATED]** Generate charts/ingress.yaml with Ingress resource for path-based routing (/ → frontend, /api → backend) using Claude
- [ ] T116 **[OPTIONAL]** Apply Ingress resource: `kubectl apply -f charts/ingress.yaml`
- [ ] T117 **[OPTIONAL]** Add todo-app.local to /etc/hosts: `echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts`
- [ ] T118 **[OPTIONAL]** Test Ingress access: Open http://todo-app.local in browser

### Performance & Scaling Tests

- [ ] T119 **[OPTIONAL]** Test frontend horizontal scaling: `kubectl scale deployment todo-frontend-deployment --replicas=3`
- [ ] T120 **[OPTIONAL]** Verify scaled frontend pods: `kubectl get pods -l app.kubernetes.io/name=frontend` (should show 3 pods)
- [ ] T121 **[OPTIONAL]** Test rolling update: `helm upgrade todo-frontend charts/frontend --set image.tag=1.0.1`
- [ ] T122 **[OPTIONAL]** Verify rolling update status: `kubectl rollout status deployment/todo-frontend-deployment`
- [ ] T123 **[OPTIONAL]** Test rollback: `helm rollback todo-frontend`
- [ ] T124 **[OPTIONAL]** Verify rollback status: `kubectl get pods -l app.kubernetes.io/name=frontend`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2 / US1)**: Depends on Setup completion - BLOCKS all deployments
- **User Story 2 (Backend)**: Depends on US1 (Minikube cluster operational)
- **User Story 3 (Frontend)**: Depends on US2 (Backend deployed and healthy)
- **User Story 4 (Validation)**: Depends on US3 (Frontend deployed and accessible)
- **Polish (Phase 6)**: Depends on US4 (System validated and operational)

### User Story Dependencies

- **US1 (Cluster Setup)**: No dependencies - foundational prerequisite
- **US2 (Backend)**: Depends on US1 (cluster must be running)
- **US3 (Frontend)**: Depends on US2 (backend service must be accessible)
- **US4 (Validation)**: Depends on US3 (full system deployed)

### Within Each User Story

- **US1**: Sequential cluster setup → addon enablement → validation
- **US2**: Dockerfiles + image builds (parallel) → Database chart generation + deployment → Backend chart generation + deployment
- **US3**: Dockerfile + image build → Frontend chart generation + deployment → Access verification
- **US4**: Smoke test script generation → Automated tests → Manual tests → Resource monitoring (parallel opportunities)

### Parallel Opportunities

#### Within User Story 2 (Backend):
```bash
# Parallel: Generate .dockerignore files
Task T017: frontend/.dockerignore
Task T018: backend/.dockerignore

# Parallel: Generate database Helm chart templates
Task T025: Chart.yaml
Task T026: values.yaml
Task T027: _helpers.tpl
Task T028: statefulset.yaml
Task T029: service.yaml
Task T030: NOTES.txt
Task T031: README.md

# Parallel: Generate backend Helm chart templates
Task T039: Chart.yaml
Task T040: values.yaml
Task T041: _helpers.tpl
Task T042: deployment.yaml
Task T043: service.yaml
Task T044: configmap.yaml
Task T045: secret.yaml
Task T046: NOTES.txt
Task T047: README.md
```

#### Within User Story 3 (Frontend):
```bash
# Parallel: Generate frontend Helm chart templates
Task T066: Chart.yaml
Task T067: values.yaml
Task T068: _helpers.tpl
Task T069: deployment.yaml
Task T070: service.yaml
Task T071: configmap.yaml
Task T072: NOTES.txt
Task T073: README.md
```

#### Within User Story 4 (Validation):
```bash
# Parallel: Resource monitoring
Task T096: kubectl top nodes
Task T097: kubectl top pods
Task T098: kubectl get pods --all-namespaces
Task T099: kagent analyze resources (if available)
Task T100: kagent audit security (if available)
```

#### Within Polish Phase:
```bash
# Parallel: Documentation updates
Task T107: README deployment overview
Task T108: README quickstart commands
Task T109: README validation commands
Task T110: README troubleshooting
Task T111: README cleanup commands

# Parallel: Script generation
Task T112: cleanup-deployment.sh
Task T113: upgrade-deployment.sh
Task T114: rollback-deployment.sh
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2 / US1: Cluster Setup (T007-T016)
3. Complete Phase 3 / US2: Backend Deployment (T017-T058)
4. **STOP and VALIDATE**: Test backend independently via `kubectl exec` curl
5. Deploy/demo backend API (optional checkpoint)

### Incremental Delivery

1. Setup + US1 (Cluster) → Cluster ready ✅
2. Add US2 (Backend) → Test independently → Backend API operational ✅
3. Add US3 (Frontend) → Test independently → Full UI accessible ✅
4. Add US4 (Validation) → Smoke tests pass → Production-ready system ✅
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers/agents:

1. Team completes Setup + US1 (Cluster) together
2. Once cluster is ready:
   - **Agent A (Gordon + Claude)**: US2 Backend (Dockerfiles + Helm charts)
   - **Agent B (Gordon + Claude)**: US3 Frontend (Dockerfiles + Helm charts) [can start after T024]
   - **Agent C (Claude)**: US4 Validation scripts (can prepare early)
3. Stories deploy sequentially but can be prepared in parallel

---

## Agent Responsibility Matrix

| Task ID | Agent | Task Type | Input | Output |
|---------|-------|-----------|-------|--------|
| T001-T006 | Claude | Setup | System check | Directories, validations |
| T007-T016 | Claude + kubectl-ai/kagent | Cluster Setup | Minikube commands | Running cluster |
| T017-T018 | Claude | File Generation | .dockerignore patterns | .dockerignore files |
| T019-T020 | **Gordon** (fallback: Claude) | Dockerfile Generation | backend/ source | backend/Dockerfile |
| T021-T024 | Claude | Docker Build & Load | Dockerfile | Docker image in Minikube |
| T025-T031 | **Claude** | Helm Chart Generation | data-model.md, contracts/ | charts/database/ |
| T032-T038 | Claude + kubectl-ai | Helm Deployment | Helm chart | Running database |
| T039-T047 | **Claude** | Helm Chart Generation | data-model.md, contracts/ | charts/backend/ |
| T048-T058 | Claude + kubectl-ai/kagent | Helm Deployment | Helm chart | Running backend |
| T059-T061 | **Gordon** (fallback: Claude) | Dockerfile Generation | frontend/ source | frontend/Dockerfile, nginx.conf |
| T062-T065 | Claude | Docker Build & Load | Dockerfile | Docker image in Minikube |
| T066-T073 | **Claude** | Helm Chart Generation | data-model.md, contracts/ | charts/frontend/ |
| T074-T085 | Claude + kubectl-ai/kagent | Helm Deployment | Helm chart | Running frontend |
| T086-T106 | **Claude** | Validation & Testing | Deployed system | Test results |
| T107-T124 | **Claude** | Documentation & Polish | Implementation artifacts | Documentation, scripts |

**Key Agents**:
- **Gordon (Docker AI)**: T019-T020, T059-T061 (Dockerfile generation)
- **Claude Sonnet 4.5**: All task orchestration, Helm chart generation, documentation
- **kubectl-ai** (optional): Deployment troubleshooting, error diagnosis
- **kagent** (optional): T016, T058, T085, T099, T100 (cluster/deployment analysis)

---

## Success Criteria Validation

| Criterion | Validated By | Tasks | Target |
|-----------|--------------|-------|--------|
| **SC-001: Deployment time < 10 min** | Manual timer | T007-T085 | Time from minikube start to frontend accessible |
| **SC-002: Pod startup < 2 min** | T035, T051, T077 | kubectl wait commands | All pods Running within 120s |
| **SC-003: Frontend access < 30 sec** | T082 | curl test | HTTP 200 response |
| **SC-004: Concurrent users** | T089-T094 | Manual UI testing | No errors with 2 users |
| **SC-005: Health checks > 99%** | T098 | kubectl get pods | All pods READY |
| **SC-006: Smoke tests 100% pass** | T088 | scripts/validate-deployment.sh | 7/7 tests pass |
| **SC-007: Teardown/redeploy** | T112 + re-run T034, T050, T076 | Cleanup + reinstall | No errors |
| **SC-008: Documentation quality** | T107-T111 | README completeness | First-attempt success |

---

## Notes

- **[P]** tasks = different files, no dependencies - can run in parallel
- **[Story]** label maps task to specific user story for traceability
- Each user story is independently completable and testable
- **[AI-GENERATED]** markers indicate tasks that require AI agent artifact generation (Gordon or Claude)
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- **Tests**: Only post-deployment smoke tests included (no pre-implementation TDD tests requested in spec)

**Total Tasks**: 124
- Setup: 6 tasks
- US1 (Cluster Setup): 10 tasks
- US2 (Backend Deployment): 42 tasks (includes database)
- US3 (Frontend Deployment): 27 tasks
- US4 (Validation): 21 tasks
- Polish: 18 tasks (12 required + 6 optional)

**Parallel Opportunities**: 40+ tasks marked with [P] can run concurrently

**MVP Scope**: US1 + US2 (56 tasks) provides functional backend API for independent testing
**Full System**: US1 + US2 + US3 (83 tasks) provides complete user-facing application
**Production-Ready**: All phases (124 tasks) includes validation, documentation, and operational scripts
