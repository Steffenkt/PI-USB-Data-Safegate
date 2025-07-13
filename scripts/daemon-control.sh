#!/bin/bash

# PI USB Data Safegate Daemon Control Script
# Provides convenient control of the daemon service

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVICE_NAME="pi-usb-safegate"
DAEMON_PATH="/usr/share/pi-usb-safegate/daemon.py"
STATUS_FILE="/var/run/pi-usb-safegate/status.json"

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

service_status() {
    print_status "Checking service status..."
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Service is running"
        
        # Show detailed status from status file
        if [[ -f "$STATUS_FILE" ]]; then
            echo
            print_status "Daemon Status:"
            python3 -c "
import json
try:
    with open('$STATUS_FILE', 'r') as f:
        status = json.load(f)
    print(f'  Status: {status.get(\"daemon_status\", \"unknown\")}')
    print(f'  Message: {status.get(\"message\", \"No message\")}')
    print(f'  Last Activity: {status.get(\"last_activity\", \"Never\")}')
    print(f'  Uptime: {status.get(\"uptime\", \"Unknown\")}')
    print(f'  Processing Count: {status.get(\"processing_count\", 0)}')
    if status.get('errors'):
        print(f'  Recent Errors: {len(status[\"errors\"])}')
except Exception as e:
    print(f'  Error reading status: {e}')
"
        fi
        
    elif systemctl is-failed --quiet "$SERVICE_NAME"; then
        print_error "Service has failed"
        systemctl status "$SERVICE_NAME" --no-pager
        
    else:
        print_warning "Service is not running"
    fi
    
    echo
    print_status "Systemd service status:"
    systemctl status "$SERVICE_NAME" --no-pager -l
}

start_service() {
    print_status "Starting PI USB Data Safegate service..."
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_warning "Service is already running"
        return 0
    fi
    
    systemctl start "$SERVICE_NAME"
    
    # Wait a moment for service to start
    sleep 2
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Service started successfully"
    else
        print_error "Failed to start service"
        systemctl status "$SERVICE_NAME" --no-pager
        exit 1
    fi
}

stop_service() {
    print_status "Stopping PI USB Data Safegate service..."
    
    if ! systemctl is-active --quiet "$SERVICE_NAME"; then
        print_warning "Service is not running"
        return 0
    fi
    
    systemctl stop "$SERVICE_NAME"
    
    # Wait for service to stop
    sleep 2
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_error "Failed to stop service"
        exit 1
    else
        print_success "Service stopped successfully"
    fi
}

restart_service() {
    print_status "Restarting PI USB Data Safegate service..."
    
    systemctl restart "$SERVICE_NAME"
    
    # Wait a moment for service to restart
    sleep 2
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Service restarted successfully"
    else
        print_error "Failed to restart service"
        systemctl status "$SERVICE_NAME" --no-pager
        exit 1
    fi
}

enable_service() {
    print_status "Enabling PI USB Data Safegate service for auto-start..."
    
    systemctl enable "$SERVICE_NAME"
    print_success "Service enabled for auto-start"
}

disable_service() {
    print_status "Disabling PI USB Data Safegate service auto-start..."
    
    systemctl disable "$SERVICE_NAME"
    print_success "Service disabled for auto-start"
}

show_logs() {
    print_status "Showing service logs..."
    
    if [[ "$1" == "follow" ]]; then
        journalctl -u "$SERVICE_NAME" -f
    else
        journalctl -u "$SERVICE_NAME" --no-pager -l
    fi
}

test_daemon() {
    print_status "Testing daemon functionality..."
    
    if [[ -f "$DAEMON_PATH" ]]; then
        python3 "$DAEMON_PATH" test
    else
        print_error "Daemon script not found: $DAEMON_PATH"
        exit 1
    fi
}

show_help() {
    echo "PI USB Data Safegate Daemon Control"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start       Start the daemon service"
    echo "  stop        Stop the daemon service"
    echo "  restart     Restart the daemon service"
    echo "  status      Show service status"
    echo "  enable      Enable auto-start on boot"
    echo "  disable     Disable auto-start on boot"
    echo "  logs        Show service logs"
    echo "  logs-follow Follow service logs in real-time"
    echo "  test        Test daemon functionality"
    echo "  help        Show this help message"
    echo
    echo "Examples:"
    echo "  sudo $0 start"
    echo "  sudo $0 status"
    echo "  sudo $0 logs-follow"
}

main() {
    check_root
    
    case "${1:-status}" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            service_status
            ;;
        enable)
            enable_service
            ;;
        disable)
            disable_service
            ;;
        logs)
            show_logs
            ;;
        logs-follow)
            show_logs follow
            ;;
        test)
            test_daemon
            ;;
        help|--help|-h)
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