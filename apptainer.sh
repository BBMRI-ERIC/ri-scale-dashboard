#!/bin/bash

# RI-SCALE Dashboard Apptainer Helper Script
# Simplified container building and running

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="ri-scale-dashboard.sif"
CONTAINER_PATH="${SCRIPT_DIR}/${CONTAINER_NAME}"
APPTAINER_DEF="${SCRIPT_DIR}/Apptainer.def"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=== RI-SCALE Dashboard Apptainer Helper ===${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

check_apptainer() {
    if ! command -v apptainer &> /dev/null; then
        print_error "Apptainer is not installed!"
        echo "Install it with:"
        echo "  Ubuntu/Debian: sudo apt-get install apptainer"
        echo "  CentOS/RHEL: sudo dnf install apptainer"
        echo "  Conda: conda install -c conda-forge apptainer"
        exit 1
    fi
    print_success "Apptainer found: $(apptainer --version)"
}

build_container() {
    print_info "Building Apptainer container..."
    
    if [ ! -f "$APPTAINER_DEF" ]; then
        print_error "Apptainer.def not found at $APPTAINER_DEF"
        exit 1
    fi

    # Prefer sudo (prompt if needed). Fallback to fakeroot.
    if command -v sudo &> /dev/null; then
        print_info "Using sudo to build container..."
        sudo -v
        sudo apptainer build "$CONTAINER_PATH" "$APPTAINER_DEF"
    else
        print_info "Attempting fakeroot build..."
        apptainer build --fakeroot "$CONTAINER_PATH" "$APPTAINER_DEF"
    fi
    
    print_success "Container built: $CONTAINER_PATH"
}

run_backend() {
    print_info "Running FastAPI backend..."
    if [ ! -f "$CONTAINER_PATH" ]; then
        print_error "Container not found. Run 'build' first."
        exit 1
    fi
    
    echo
    print_info "Backend starting on http://0.0.0.0:8000"
    echo "Press Ctrl+C to stop"
    echo
    
    apptainer run "$CONTAINER_PATH"
}

run_frontend() {
    print_info "Running Vue.js frontend..."
    if [ ! -f "$CONTAINER_PATH" ]; then
        print_error "Container not found. Run 'build' first."
        exit 1
    fi
    
    echo
    print_info "Frontend starting on http://localhost:3000"
    echo "Press Ctrl+C to stop"
    echo
    
    apptainer exec --writable-tmpfs "$CONTAINER_PATH" sh -c "cd /opt/ri-scale/frontend && npm run dev"
}

run_shell() {
    print_info "Opening interactive shell..."
    if [ ! -f "$CONTAINER_PATH" ]; then
        print_error "Container not found. Run 'build' first."
        exit 1
    fi
    
    apptainer shell "$CONTAINER_PATH"
}

run_command() {
    if [ ! -f "$CONTAINER_PATH" ]; then
        print_error "Container not found. Run 'build' first."
        exit 1
    fi
    
    apptainer exec "$CONTAINER_PATH" "$@"
}

run_dps_pipeline() {
    if [ ! -f "$CONTAINER_PATH" ]; then
        print_error "Container not found. Run 'build' first."
        exit 1
    fi
    
    print_info "Running DPS pipeline..."
    apptainer exec "$CONTAINER_PATH" \
        python /opt/ri-scale/backend/app/services/dps_service/dps_service.py \
        -m /opt/ri-scale/backend/app/services/dps_service/example_manifest.yaml -v
}

run_all() {
    print_info "Starting backend and frontend services..."
    if [ ! -f "$CONTAINER_PATH" ]; then
        print_error "Container not found. Run 'build' first."
        exit 1
    fi
    
    echo
    print_info "Backend starting on http://0.0.0.0:8000"
    print_info "Frontend starting on http://localhost:5173"
    echo
    print_info "Press Ctrl+C to stop all services"
    echo
    
    # Start backend in background
    apptainer run "$CONTAINER_PATH" &
    BACKEND_PID=$!
    
    # Give backend a moment to start
    sleep 2
    
    # Start frontend in background
    apptainer exec "$CONTAINER_PATH" npm run dev --prefix /opt/ri-scale/frontend &
    FRONTEND_PID=$!
    
    # Trap Ctrl+C to kill both processes
    trap "echo ''; print_info 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
    
    # Wait for both processes
    wait $BACKEND_PID $FRONTEND_PID
}

run_vscode_server() {
    print_info "Starting VS Code Server..."
    if [ ! -f "$CONTAINER_PATH" ]; then
        print_error "Container not found. Run 'build' first."
        exit 1
    fi
    
    local PORT="${1:-8443}"
    
    echo
    print_info "VS Code Server starting on http://0.0.0.0:$PORT"
    echo
    print_info "Open in browser: http://localhost:$PORT"
    print_info "Project folder: /opt/ri-scale"
    print_info "Press Ctrl+C to stop"
    echo
    
    apptainer exec "$CONTAINER_PATH" bash -c "cd /opt/ri-scale && code serve-web \
        --accept-server-license-terms \
        --host 0.0.0.0 \
        --port $PORT"
}

run_vscode_tunnel() {
    print_info "Starting VS Code Tunnel..."
    if [ ! -f "$CONTAINER_PATH" ]; then
        print_error "Container not found. Run 'build' first."
        exit 1
    fi
    
    echo
    print_info "Creating secure tunnel for remote access..."
    echo
    
    apptainer exec "$CONTAINER_PATH" code tunnel \
        --accept-server-license-terms
}

show_status() {
    print_header
    
    if [ -f "$CONTAINER_PATH" ]; then
        SIZE=$(du -h "$CONTAINER_PATH" | cut -f1)
        MODIFIED=$(stat -f %Sm -t "%Y-%m-%d %H:%M:%S" "$CONTAINER_PATH" 2>/dev/null || stat -c %y "$CONTAINER_PATH" | cut -d' ' -f1-2)
        print_success "Container exists: $CONTAINER_PATH"
        print_info "Size: $SIZE"
        print_info "Modified: $MODIFIED"
    else
        print_error "Container not found: $CONTAINER_PATH"
        print_info "Run './apptainer.sh build' to create it"
    fi
    
    echo
    check_apptainer
}

show_help() {
    print_header
    cat << 'EOF'
Usage: ./apptainer.sh [COMMAND] [OPTIONS]

Commands:
  build              Build the Apptainer container
  start              Start both backend and frontend services
  backend            Run the FastAPI backend (http://0.0.0.0:8000)
  frontend           Run the Vue.js frontend (http://localhost:5173)
  vscode             Start VS Code Server (web-based, default port 8443)
  vscode-tunnel      Create VS Code secure tunnel for remote access
  shell              Open interactive shell in container
  dps-pipeline       Run DPS pipeline with example manifest
  status             Show container status
  exec COMMAND       Execute arbitrary command in container
  help               Show this help message

Examples:
  ./apptainer.sh build
  ./apptainer.sh start              # Start both services
  ./apptainer.sh backend
  ./apptainer.sh frontend
  ./apptainer.sh vscode             # VS Code at https://localhost:8443
  ./apptainer.sh vscode 9443        # VS Code at custom port
  ./apptainer.sh vscode-tunnel      # Remote access tunnel
  ./apptainer.sh shell
  ./apptainer.sh exec code --version
  ./apptainer.sh exec python --version

For more information, see APPTAINER_GUIDE.md or VSCODE_CLI_GUIDE.md
EOF
}

main() {
    check_apptainer
    
    case "${1:-help}" in
        build)
            print_header
            build_container
            ;;
        start)
            print_header
            run_all
            ;;
        backend)
            print_header
            run_backend
            ;;
        frontend)
            print_header
            run_frontend
            ;;
        shell)
            print_header
            run_shell
            ;;
        vscode)
            print_header
            shift
            run_vscode_server "$@"
            ;;
        vscode-tunnel)
            print_header
            run_vscode_tunnel
            ;;
        dps-pipeline)
            print_header
            run_dps_pipeline
            ;;
        status)
            show_status
            ;;
        exec)
            shift
            run_command "$@"
            ;;
        help|-h|--help)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

main "$@"
