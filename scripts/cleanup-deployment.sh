#!/bin/bash
# =============================================================================
# Phase 4 - Cleanup Deployment Script
# Safely tears down all Kubernetes resources deployed via Helm
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

FORCE=false
KEEP_PVC=false
DELETE_CLUSTER=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f)
            FORCE=true
            shift
            ;;
        --keep-pvc)
            KEEP_PVC=true
            shift
            ;;
        --delete-cluster)
            DELETE_CLUSTER=true
            shift
            ;;
        --help|-h)
            echo "Usage: cleanup-deployment.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force, -f        Skip confirmation prompts"
            echo "  --keep-pvc         Keep persistent volume claims (database data)"
            echo "  --delete-cluster   Also delete the Minikube cluster"
            echo "  --help, -h         Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo ""
echo "=============================================="
echo "  Phase 4 - Deployment Cleanup"
echo "  Todo AI Chatbot - Kubernetes Teardown"
echo "=============================================="
echo ""

# Confirmation
if [ "$FORCE" = false ]; then
    echo -e "${YELLOW}WARNING: This will remove all deployed resources.${NC}"
    if [ "$DELETE_CLUSTER" = true ]; then
        echo -e "${RED}WARNING: --delete-cluster will destroy the entire Minikube cluster!${NC}"
    fi
    echo ""
    read -p "Are you sure you want to continue? (y/N): " CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo "Cleanup cancelled."
        exit 0
    fi
fi

# ─────────────────────────────────────────────────
# Step 1: Uninstall Helm Releases (reverse order)
# ─────────────────────────────────────────────────
echo ""
echo -e "${CYAN}[1/4] Uninstalling Helm releases...${NC}"

# Frontend first (depends on backend)
if helm status todo-frontend &>/dev/null; then
    echo "  Removing todo-frontend..."
    helm uninstall todo-frontend --wait
    echo -e "  ${GREEN}todo-frontend removed${NC}"
else
    echo -e "  ${YELLOW}todo-frontend not found (skipped)${NC}"
fi

# Backend second (depends on database)
if helm status todo-backend &>/dev/null; then
    echo "  Removing todo-backend..."
    helm uninstall todo-backend --wait
    echo -e "  ${GREEN}todo-backend removed${NC}"
else
    echo -e "  ${YELLOW}todo-backend not found (skipped)${NC}"
fi

# Database last
if helm status todo-database &>/dev/null; then
    echo "  Removing todo-database..."
    helm uninstall todo-database --wait
    echo -e "  ${GREEN}todo-database removed${NC}"
else
    echo -e "  ${YELLOW}todo-database not found (skipped)${NC}"
fi

# ─────────────────────────────────────────────────
# Step 2: Cleanup PVCs
# ─────────────────────────────────────────────────
echo ""
echo -e "${CYAN}[2/4] Cleaning up persistent volume claims...${NC}"

if [ "$KEEP_PVC" = true ]; then
    echo -e "  ${YELLOW}Keeping PVCs (--keep-pvc flag set)${NC}"
else
    PVC_COUNT=$(kubectl get pvc --no-headers 2>/dev/null | wc -l)
    if [ "$PVC_COUNT" -gt 0 ]; then
        echo "  Found $PVC_COUNT PVC(s), removing..."
        kubectl delete pvc --all --wait=true
        echo -e "  ${GREEN}All PVCs removed${NC}"
    else
        echo -e "  ${YELLOW}No PVCs found (skipped)${NC}"
    fi
fi

# ─────────────────────────────────────────────────
# Step 3: Verify cleanup
# ─────────────────────────────────────────────────
echo ""
echo -e "${CYAN}[3/4] Verifying cleanup...${NC}"

# Wait for pods to terminate
echo "  Waiting for pods to terminate..."
kubectl wait --for=delete pod -l app.kubernetes.io/managed-by=Helm --timeout=60s 2>/dev/null || true

REMAINING_PODS=$(kubectl get pods --no-headers 2>/dev/null | grep -E "todo-" | wc -l)
REMAINING_SVC=$(kubectl get svc --no-headers 2>/dev/null | grep -E "todo-" | wc -l)
REMAINING_HELM=$(helm list --short 2>/dev/null | grep -E "todo-" | wc -l)

if [ "$REMAINING_PODS" -eq 0 ] && [ "$REMAINING_SVC" -eq 0 ] && [ "$REMAINING_HELM" -eq 0 ]; then
    echo -e "  ${GREEN}All resources cleaned up successfully${NC}"
else
    echo -e "  ${YELLOW}Some resources may still be terminating:${NC}"
    [ "$REMAINING_PODS" -gt 0 ] && echo "    Pods: $REMAINING_PODS remaining"
    [ "$REMAINING_SVC" -gt 0 ] && echo "    Services: $REMAINING_SVC remaining"
    [ "$REMAINING_HELM" -gt 0 ] && echo "    Helm releases: $REMAINING_HELM remaining"
fi

# ─────────────────────────────────────────────────
# Step 4: Optionally delete cluster
# ─────────────────────────────────────────────────
echo ""
echo -e "${CYAN}[4/4] Cluster management...${NC}"

if [ "$DELETE_CLUSTER" = true ]; then
    echo "  Deleting Minikube cluster..."
    minikube delete
    echo -e "  ${GREEN}Minikube cluster deleted${NC}"
else
    echo -e "  ${YELLOW}Minikube cluster preserved (use --delete-cluster to remove)${NC}"
    echo "  To stop: minikube stop"
    echo "  To delete: minikube delete"
fi

# ─────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────
echo ""
echo "=============================================="
echo -e "  ${GREEN}Cleanup Complete!${NC}"
echo "=============================================="
echo ""
echo "  To redeploy, follow PHASE4-RUN-COMMANDS.md"
echo "  Or run: scripts/check-prerequisites.sh first"
echo ""
