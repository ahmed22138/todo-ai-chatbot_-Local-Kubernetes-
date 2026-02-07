#!/bin/bash
# =============================================================================
# Phase 4 - Rollback Deployment Script
# Rolls back Helm releases to a previous revision
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

COMPONENT=""
REVISION=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --component)
            COMPONENT="$2"
            shift 2
            ;;
        --revision)
            REVISION="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: rollback-deployment.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --component NAME     Component to rollback (frontend|backend|database|all)"
            echo "  --revision NUM       Specific revision to rollback to (default: previous)"
            echo "  --help, -h           Show this help message"
            echo ""
            echo "Examples:"
            echo "  # Rollback frontend to previous version"
            echo "  ./rollback-deployment.sh --component frontend"
            echo ""
            echo "  # Rollback backend to specific revision"
            echo "  ./rollback-deployment.sh --component backend --revision 2"
            echo ""
            echo "  # Rollback all components"
            echo "  ./rollback-deployment.sh --component all"
            echo ""
            echo "  # View history first"
            echo "  helm history todo-frontend"
            echo "  helm history todo-backend"
            echo "  helm history todo-database"
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
echo "  Phase 4 - Deployment Rollback"
echo "  Todo AI Chatbot - Helm Rollback"
echo "=============================================="
echo ""

if [ -z "$COMPONENT" ]; then
    echo -e "${RED}Error: --component is required${NC}"
    echo "Usage: rollback-deployment.sh --component <frontend|backend|database|all>"
    exit 1
fi

# Helper: rollback a single release
rollback_release() {
    local RELEASE=$1
    local TARGET_REV=${2:-""}

    if ! helm status "$RELEASE" &>/dev/null; then
        echo -e "  ${YELLOW}$RELEASE not found (skipped)${NC}"
        return 0
    fi

    echo -e "${CYAN}Rolling back $RELEASE...${NC}"

    # Show history
    echo "  Release history:"
    helm history "$RELEASE" --max 5 2>/dev/null | while IFS= read -r line; do
        echo "    $line"
    done
    echo ""

    # Current revision
    CURRENT_REV=$(helm history "$RELEASE" --max 1 -o json 2>/dev/null | grep -o '"revision":[0-9]*' | head -1 | cut -d: -f2 || echo "?")
    echo "  Current revision: $CURRENT_REV"

    # Perform rollback
    if [ -n "$TARGET_REV" ]; then
        echo "  Rolling back to revision: $TARGET_REV"
        if helm rollback "$RELEASE" "$TARGET_REV" --wait --timeout=120s; then
            echo -e "  ${GREEN}Rolled back $RELEASE to revision $TARGET_REV${NC}"
            return 0
        else
            echo -e "  ${RED}Rollback FAILED for $RELEASE${NC}"
            return 1
        fi
    else
        # Rollback to previous (no revision = previous)
        echo "  Rolling back to previous revision..."
        if helm rollback "$RELEASE" --wait --timeout=120s; then
            echo -e "  ${GREEN}Rolled back $RELEASE to previous revision${NC}"
            return 0
        else
            echo -e "  ${RED}Rollback FAILED for $RELEASE${NC}"
            return 1
        fi
    fi
}

# ─────────────────────────────────────────────────
# Perform rollbacks
# ─────────────────────────────────────────────────
ROLLBACK_COUNT=0
FAIL_COUNT=0

case "$COMPONENT" in
    frontend)
        rollback_release "todo-frontend" "$REVISION" && ROLLBACK_COUNT=$((ROLLBACK_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))
        ;;
    backend)
        rollback_release "todo-backend" "$REVISION" && ROLLBACK_COUNT=$((ROLLBACK_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))
        ;;
    database)
        rollback_release "todo-database" "$REVISION" && ROLLBACK_COUNT=$((ROLLBACK_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))
        ;;
    all)
        echo -e "${YELLOW}Rolling back ALL components (frontend -> backend -> database)${NC}"
        echo ""
        rollback_release "todo-frontend" "$REVISION" && ROLLBACK_COUNT=$((ROLLBACK_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))
        echo ""
        rollback_release "todo-backend" "$REVISION" && ROLLBACK_COUNT=$((ROLLBACK_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))
        echo ""
        rollback_release "todo-database" "$REVISION" && ROLLBACK_COUNT=$((ROLLBACK_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))
        ;;
    *)
        echo -e "${RED}Unknown component: $COMPONENT${NC}"
        echo "Valid: frontend, backend, database, all"
        exit 1
        ;;
esac

# ─────────────────────────────────────────────────
# Post-rollback verification
# ─────────────────────────────────────────────────
echo ""
echo -e "${CYAN}Post-rollback pod status:${NC}"
echo ""
kubectl get pods
echo ""

# Wait for pods to be ready
echo "Waiting for pods to stabilize..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/managed-by=Helm --timeout=120s 2>/dev/null || true
echo ""

# ─────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────
echo "=============================================="
if [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "  ${GREEN}Rollback Complete! ($ROLLBACK_COUNT component(s) rolled back)${NC}"
else
    echo -e "  ${RED}Rollback had issues: $FAIL_COUNT failed, $ROLLBACK_COUNT succeeded${NC}"
fi
echo "=============================================="
echo ""
echo "  Verify: bash scripts/validate-deployment.sh"
echo ""
