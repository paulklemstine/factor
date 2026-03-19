#!/bin/bash
# Multi-Agent Research Team Launcher
# ===================================
# Launches the agent team for exploring moonshot hypotheses,
# zeta function connections, cross-domain applications, and
# compression algorithms.
#
# Usage:
#   ./launch_agents.sh [mode] [options]
#
# Modes:
#   single     - Run one full cycle (default)
#   forever    - Run continuously until stopped
#   report     - Generate report from checkpoint
#
# Examples:
#   ./launch_agents.sh single
#   ./launch_agents.sh forever --hours 24
#   ./launch_agents.sh report

set -e

# Configuration
MEMORY_LIMIT=5500  # MB (keep under 6GB)
CHECKPOINT_DIR="agent_checkpoints"
PYTHON=${PYTHON:-python3}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     MULTI-AGENT RESEARCH TEAM — PYTHAGOREAN EXPLORATION       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python
if ! command -v $PYTHON &> /dev/null; then
    echo -e "${RED}Error: Python3 not found${NC}"
    exit 1
fi

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"

check_module() {
    if $PYTHON -c "import $1" 2>/dev/null; then
        echo -e "  ✓ $1"
    else
        echo -e "  ✗ $1 (missing)"
        MISSING+=("$1")
    fi
}

MISSING=()
check_module "numpy"
check_module "gmpy2"
check_module "mpmath"

if [ ${#MISSING[@]} -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}Missing modules. Install with:${NC}"
    echo "  pip install numpy gmpy2 mpmath"
    echo ""
    echo "On Ubuntu/WSL:"
    echo "  sudo apt install python3-numpy python3-gmpy2"
    echo ""
fi

echo ""

# Parse arguments
MODE=${1:-single}
shift || true

case $MODE in
    single)
        echo -e "${GREEN}Mode: Single Cycle${NC}"
        $PYTHON agent_manager.py --mode single \
            --memory-limit $MEMORY_LIMIT \
            --checkpoint-dir $CHECKPOINT_DIR \
            --output research_report.md \
            "$@"
        ;;
    
    forever)
        echo -e "${GREEN}Mode: Continuous (until stopped)${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop gracefully${NC}"
        $PYTHON agent_manager.py --mode forever \
            --memory-limit $MEMORY_LIMIT \
            --checkpoint-dir $CHECKPOINT_DIR \
            "$@"
        ;;
    
    report)
        echo -e "${GREEN}Mode: Generate Report${NC}"
        $PYTHON agent_manager.py --mode report \
            --checkpoint-dir $CHECKPOINT_DIR \
            --output research_report.md
        ;;
    
    *)
        echo "Unknown mode: $MODE"
        echo "Usage: $0 [single|forever|report] [options]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Done!${NC}"
echo "Report: research_report.md"
echo "Checkpoints: $CHECKPOINT_DIR/"
