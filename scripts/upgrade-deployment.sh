#!/bin/bash
# =============================================================================
# Phase 4 - Upgrade Deployment Script
# Performs rolling upgrades of Helm releases with new image tags
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Defaults
FRONTEND_TAG=""
BACKEND_TAG=""
COMPONENT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --frontend-tag)
            FRONTEND_TAG="$2"
            shift 2
            ;;
        --backend-tag)
            BACKEND_TAG="$2"
            shift 2
            ;;
        --component)
            COMPONENT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: upgrade-deployment.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --frontend-tag TAG   New frontend image tag (e.g., 2.0.0)"
            echo "  --backend-tag TAG    New backend image tag (e.g., 2.0.0)"
            echo "  --component NAME     Upgrade specific component (frontend|backend|database|all)"
            echo "  --help, -h           Show this help message"
            echo ""
            echo "Examples:"
            echo "  # Upgrade frontend to new version"
            echo "  ./upgrade-deployment.sh --component frontend --frontend-tag 2.0.0"
            echo ""
            echo "  # Upgrade both frontend and backend"
            echo "  ./upgrade-deployment.sh --frontend-tag 2.0.0 --backend-tag 2.0.0"
            echo ""
            echo "  # Upgrade all components with current values"
            echo "  ./upgrade-deployment.sh --component all"
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
echo "  Phase 4 - Deployment Upgrade"
echo "  Todo AI Chatbot - Rolling Update"
echo "=============================================="
echo ""

# Helper: upgrade a single component
upgrade_component() {
    local RELEASE=$1
    local CHART=$2
    local EXTRA_ARGS=${3:-""}

    echo -e "${CYAN}Upgrading $RELEASE...${NC}"

    # Show current revision
    CURRENT_REV=$(helm history "$RELEASE" --max 1 -o json 2>/dev/null | grep -o '"revision":[0-9]*' | head -1 | cut -d: -f2 || echo "?")
    echo "  Current revision: $CURRENT_REV"

    # Perform upgrade
    if helm upgrade "$RELEASE" "$CHART" $EXTRA_ARGS --wait --timeout=120s; then
        NEW_REV=$(helm history "$RELEASE" --max 1 -o json 2>/dev/null | grep -o '"revision":[0-9]*' | head -1 | cut -d: -f2 || echo "?")
        echo -e "  ${GREEN}Upgraded to revision: $NEW_REV${NC}"
        return 0
    else
        echo -e "  ${RED}Upgrade FAILED for $RELEASE${NC}"
        echo -e "  ${YELLOW}Rolling back...${NC}"
        helm rollback "$RELEASE" --wait
        echo -e "  ${GREEN}Rolled back to previous version${NC}"
        return 1
    fi
}

# ─────────────────────────────────────────────────
# Pre-flight checks
# ─────────────────────────────────────────────────
echo -e "${CYAN}Pre-flight checks...${NC}"

# Verify cluster is running
if ! minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
    echo -e "${RED}Minikube is not running. Start it first: minikube start${NC}"
    exit 1
fi
echo -e "  ${GREEN}Cluster is running${NC}"

# List current releases
echo ""
echo "Current Helm releases:"
helm list --short 2>/dev/null | while read -r line; do
    echo "  - $line"
done
echo ""

# ─────────────────────────────────────────────────
# Perform upgrades
# ─────────────────────────────────────────────────
UPGRADE_COUNT=0
FAIL_COUNT=0

# Database upgrade
if [ "$COMPONENT" = "database" ] || [ "$COMPONENT" = "all" ] || [ -z "$COMPONENT" -a -z "$FRONTEND_TAG" -a -z "$BACKEND_TAG" ]; then
    if [ "$COMPONENT" = "database" ] || [ "$COMPONENT" = "all" ]; then
        if helm status todo-database &>/dev/null; then
            upgrade_component "todo-database" "charts/database" && UPGRADE_COUNT=$((UPGRADE_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))
            echo ""
        fi
    fi
fi

# Backend upgrade
if [ "$COMPONENT" = "backend" ] || [ "$COMPONENT" = "all" ] || [ -n "$BACKEND_TAG" ]; then
    if helm status todo-backend &>/dev/null; then
        EXTRA=""
        if [ -n "$BACKEND_TAG" ]; then
            EXTRA="--set image.tag=$BACKEND_TAG"
            echo "  New backend image tag: $BACKEND_TAG"

            # Build and load new image if tag changed
            echo "  Building new backend image..."
            docker build -t "todo-backend:$BACKEND_TAG" ./backend
            minikube image load "todo-backend:$BACKEND_TAG"
        fi
        upgrade_component "todo-backend" "charts/backend" "$EXTRA" && UPGRADE_COUNT=$((UPGRADE_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))
        echo ""
    else
        echo -e "${YELLOW}todo-backend release not found (skipped)${NC}"
    fi
fi

# Frontend upgrade
if [ "$COMPONENT" = "frontend" ] || [ "$COMPONENT" = "all" ] || [ -n "$FRONTEND_TAG" ]; then
    if helm status todo-frontend &>/dev/null; then
        EXTRA=""
        if [ -n "$FRONTEND_TAG" ]; then
            EXTRA="--set image.tag=$FRONTEND_TAG"
            echo "  New frontend image tag: $FRONTEND_TAG"

            # Build and load new image if tag changed
            echo "  Building new frontend image..."
            docker build -t "todo-frontend:$FRONTEND_TAG" ./frontend
            minikube image load "todo-frontend:$FRONTEND_TAG"
        fi
        upgrade_component "todo-frontend" "charts/frontend" "$EXTRA" && UPGRADE_COUNT=$((UPGRADE_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))
        echo ""
    else
        echo -e "${YELLOW}todo-frontend release not found (skipped)${NC}"
    fi
fi

# ─────────────────────────────────────────────────
# Post-upgrade verification
# ─────────────────────────────────────────────────
echo -e "${CYAN}Post-upgrade verification...${NC}"
echo ""
kubectl get pods
echo ""

# ─────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────
echo ""
echo "=============================================="
if [ "$FAIL_COUNT" -eq 0 ] && [ "$UPGRADE_COUNT" -gt 0 ]; then
    echo -e "  ${GREEN}Upgrade Complete! ($UPGRADE_COUNT component(s) upgraded)${NC}"
elif [ "$FAIL_COUNT" -gt 0 ]; then
    echo -e "  ${RED}Upgrade had failures: $FAIL_COUNT failed, $UPGRADE_COUNT succeeded${NC}"
else
    echo -e "  ${YELLOW}No components were upgraded. Use --component or --*-tag flags.${NC}"
fi
echo "=============================================="
echo ""
echo "  Verify: bash scripts/validate-deployment.sh"
echo "  Rollback: bash scripts/rollback-deployment.sh --component <name>"
echo ""
