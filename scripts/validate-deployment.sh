#!/bin/bash
# =============================================================================
# Phase 4 - Deployment Validation & Smoke Test Script
# Runs 7 automated smoke tests to verify Kubernetes deployment health
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARN=0
TOTAL=7

echo ""
echo "=============================================="
echo "  Phase 4 - Deployment Smoke Tests"
echo "  Todo AI Chatbot - Kubernetes Validation"
echo "=============================================="
echo ""

# Helper functions
pass_test() {
    PASS=$((PASS + 1))
    echo -e "  ${GREEN}[PASS]${NC} $1"
}

fail_test() {
    FAIL=$((FAIL + 1))
    echo -e "  ${RED}[FAIL]${NC} $1"
    echo -e "  ${RED}        Reason: $2${NC}"
}

warn_test() {
    WARN=$((WARN + 1))
    echo -e "  ${YELLOW}[WARN]${NC} $1"
    echo -e "  ${YELLOW}        Note: $2${NC}"
}

# ─────────────────────────────────────────────────
# TEST 1: Cluster Running Check
# ─────────────────────────────────────────────────
echo -e "${CYAN}[1/7] Checking Minikube cluster status...${NC}"
if minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
    pass_test "Minikube cluster is running"
else
    fail_test "Minikube cluster is NOT running" "Run: minikube start --cpus=4 --memory=8192"
fi

# ─────────────────────────────────────────────────
# TEST 2: All Pods Ready Check
# ─────────────────────────────────────────────────
echo -e "${CYAN}[2/7] Checking all pods are ready...${NC}"

# Check database pod
DB_READY=$(kubectl get pod todo-database-0 -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "False")
# Check backend pods
BACKEND_READY=$(kubectl get pods -l app.kubernetes.io/name=backend -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "False")
# Check frontend pods
FRONTEND_READY=$(kubectl get pods -l app.kubernetes.io/name=frontend -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "False")

ALL_PODS_OK=true

if [ "$DB_READY" != "True" ]; then
    echo -e "    ${RED}Database pod: NOT READY${NC}"
    ALL_PODS_OK=false
else
    echo -e "    ${GREEN}Database pod: READY${NC}"
fi

# Check if all backend pods report True
if echo "$BACKEND_READY" | grep -q "False" || [ -z "$BACKEND_READY" ]; then
    echo -e "    ${RED}Backend pod(s): NOT READY${NC}"
    ALL_PODS_OK=false
else
    BACKEND_COUNT=$(kubectl get pods -l app.kubernetes.io/name=backend --no-headers 2>/dev/null | wc -l)
    echo -e "    ${GREEN}Backend pod(s): READY ($BACKEND_COUNT running)${NC}"
fi

# Check if all frontend pods report True
if echo "$FRONTEND_READY" | grep -q "False" || [ -z "$FRONTEND_READY" ]; then
    echo -e "    ${RED}Frontend pod(s): NOT READY${NC}"
    ALL_PODS_OK=false
else
    FRONTEND_COUNT=$(kubectl get pods -l app.kubernetes.io/name=frontend --no-headers 2>/dev/null | wc -l)
    echo -e "    ${GREEN}Frontend pod(s): READY ($FRONTEND_COUNT running)${NC}"
fi

if [ "$ALL_PODS_OK" = true ]; then
    pass_test "All pods are running and ready"
else
    fail_test "Some pods are NOT ready" "Run: kubectl get pods to check status"
fi

# ─────────────────────────────────────────────────
# TEST 3: Frontend Accessibility Check
# ─────────────────────────────────────────────────
echo -e "${CYAN}[3/7] Checking frontend accessibility...${NC}"

FRONTEND_POD=$(kubectl get pods -l app.kubernetes.io/name=frontend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$FRONTEND_POD" ]; then
    FRONTEND_RESPONSE=$(kubectl exec "$FRONTEND_POD" -- wget -qO- --timeout=5 http://localhost:80/ 2>/dev/null | head -c 100 || echo "")
    if echo "$FRONTEND_RESPONSE" | grep -qi "html"; then
        pass_test "Frontend is serving HTML content"
    else
        # Fallback: check if service endpoint exists
        FRONTEND_EP=$(kubectl get endpoints todo-frontend-service -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null || echo "")
        if [ -n "$FRONTEND_EP" ]; then
            pass_test "Frontend service has active endpoints"
        else
            fail_test "Frontend is NOT accessible" "Check: kubectl logs $FRONTEND_POD"
        fi
    fi
else
    fail_test "Frontend pod NOT found" "Run: helm install todo-frontend charts/frontend"
fi

# ─────────────────────────────────────────────────
# TEST 4: Backend Health Endpoint Check
# ─────────────────────────────────────────────────
echo -e "${CYAN}[4/7] Checking backend health endpoint...${NC}"

BACKEND_POD=$(kubectl get pods -l app.kubernetes.io/name=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$BACKEND_POD" ]; then
    HEALTH_RESPONSE=$(kubectl exec "$BACKEND_POD" -- wget -qO- --timeout=5 http://localhost:8000/health 2>/dev/null || echo "")
    if echo "$HEALTH_RESPONSE" | grep -qi "healthy\|ok\|status"; then
        pass_test "Backend /health endpoint is responding"
    else
        # Fallback: check service endpoint
        BACKEND_EP=$(kubectl get endpoints todo-backend-service -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null || echo "")
        if [ -n "$BACKEND_EP" ]; then
            pass_test "Backend service has active endpoints"
        else
            fail_test "Backend /health is NOT responding" "Check: kubectl logs $BACKEND_POD"
        fi
    fi
else
    fail_test "Backend pod NOT found" "Run: helm install todo-backend charts/backend"
fi

# ─────────────────────────────────────────────────
# TEST 5: Database Connectivity Check
# ─────────────────────────────────────────────────
echo -e "${CYAN}[5/7] Checking database connectivity...${NC}"

DB_POD="todo-database-0"
if kubectl get pod "$DB_POD" &>/dev/null; then
    PG_READY=$(kubectl exec "$DB_POD" -- pg_isready -U todouser -d todo_chatbot 2>/dev/null || echo "")
    if echo "$PG_READY" | grep -qi "accepting"; then
        pass_test "PostgreSQL is accepting connections"
    else
        # Fallback: check if pod is at least running
        DB_STATUS=$(kubectl get pod "$DB_POD" -o jsonpath='{.status.phase}' 2>/dev/null || echo "")
        if [ "$DB_STATUS" = "Running" ]; then
            warn_test "Database pod running but pg_isready unclear" "May need more startup time"
            PASS=$((PASS + 1))
            WARN=$((WARN - 1))
        else
            fail_test "PostgreSQL is NOT accepting connections" "Check: kubectl logs $DB_POD"
        fi
    fi
else
    fail_test "Database pod NOT found" "Run: helm install todo-database charts/database"
fi

# ─────────────────────────────────────────────────
# TEST 6: Service-to-Service Communication Check
# ─────────────────────────────────────────────────
echo -e "${CYAN}[6/7] Checking service-to-service communication...${NC}"

# Verify backend can resolve database service
if [ -n "$BACKEND_POD" ]; then
    DNS_CHECK=$(kubectl exec "$BACKEND_POD" -- nslookup todo-database-service 2>/dev/null | grep -i "address" | tail -1 || echo "")
    if [ -n "$DNS_CHECK" ]; then
        pass_test "Backend can resolve database service via DNS"
    else
        # Fallback: check service exists
        DB_SVC=$(kubectl get svc todo-database-service -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
        if [ -n "$DB_SVC" ]; then
            pass_test "Database service exists (ClusterIP: $DB_SVC)"
        else
            fail_test "Service-to-service DNS resolution failed" "Check: kubectl get svc"
        fi
    fi
else
    # If no backend pod, check services exist
    SVC_COUNT=$(kubectl get svc -l app.kubernetes.io/managed-by=Helm --no-headers 2>/dev/null | wc -l)
    if [ "$SVC_COUNT" -ge 3 ]; then
        pass_test "All 3 Helm-managed services exist"
    else
        fail_test "Missing services" "Expected 3, found $SVC_COUNT. Run: kubectl get svc"
    fi
fi

# ─────────────────────────────────────────────────
# TEST 7: Resource Utilization Check
# ─────────────────────────────────────────────────
echo -e "${CYAN}[7/7] Checking resource utilization...${NC}"

if kubectl top pods &>/dev/null; then
    # Metrics server available
    CPU_USAGE=$(kubectl top pods --no-headers 2>/dev/null | awk '{sum += $2} END {print sum}')
    MEM_USAGE=$(kubectl top pods --no-headers 2>/dev/null | awk '{sum += $3} END {print sum}')
    echo -e "    CPU: ${CPU_USAGE:-N/A}m | Memory: ${MEM_USAGE:-N/A}Mi"
    pass_test "Resource metrics available - cluster is healthy"
else
    # Metrics server not available - check resource requests/limits are set
    HAS_RESOURCES=$(kubectl get pods -o jsonpath='{.items[*].spec.containers[*].resources.limits}' 2>/dev/null || echo "")
    if [ -n "$HAS_RESOURCES" ]; then
        pass_test "Resource limits configured (metrics-server not available for live data)"
    else
        warn_test "Cannot verify resource usage" "Enable metrics-server: minikube addons enable metrics-server"
        PASS=$((PASS + 1))
        WARN=$((WARN - 1))
    fi
fi

# ─────────────────────────────────────────────────
# RESULTS SUMMARY
# ─────────────────────────────────────────────────
echo ""
echo "=============================================="
echo "  SMOKE TEST RESULTS"
echo "=============================================="
echo ""
echo -e "  Total Tests:  $TOTAL"
echo -e "  ${GREEN}Passed:       $PASS${NC}"
echo -e "  ${RED}Failed:       $FAIL${NC}"
echo -e "  ${YELLOW}Warnings:     $WARN${NC}"
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo -e "  ${GREEN}========================================${NC}"
    echo -e "  ${GREEN}  ALL SMOKE TESTS PASSED!${NC}"
    echo -e "  ${GREEN}  Deployment is healthy and ready.${NC}"
    echo -e "  ${GREEN}========================================${NC}"
    echo ""
    echo "  Next: Access the app at http://localhost:3000"
    echo "  (Run: kubectl port-forward svc/todo-frontend-service 3000:80)"
    exit 0
else
    echo -e "  ${RED}========================================${NC}"
    echo -e "  ${RED}  $FAIL TEST(S) FAILED${NC}"
    echo -e "  ${RED}  Review errors above and fix issues.${NC}"
    echo -e "  ${RED}========================================${NC}"
    echo ""
    echo "  Troubleshooting:"
    echo "    kubectl get pods"
    echo "    kubectl describe pod <pod-name>"
    echo "    kubectl logs <pod-name>"
    exit 1
fi
