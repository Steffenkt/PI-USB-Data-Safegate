#!/bin/bash

# PI USB Data Safegate - Uninstall Script
# This script removes the application and optionally cleans up configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Application info
APP_NAME="PI USB Data Safegate"
PACKAGE_NAME="pi-usb-safegate"

# Functions
print_header() {
    echo -e "${BLUE}=================================================================================${NC}"
    echo -e "${BLUE}                      $APP_NAME Uninstaller${NC}"
    echo -e "${BLUE}=================================================================================${NC}"
    echo
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_if_installed() {
    if ! dpkg -l | grep -q "$PACKAGE_NAME"; then
        print_warning "Package $PACKAGE_NAME is not installed"
        
        # Check if manually installed
        if [[ -d "/usr/share/pi-usb-safegate" ]]; then
            print_info "Found manual installation, will clean up"
            return 0
        else
            print_error "No installation found"
            exit 1
        fi
    fi
    
    print_info "Package $PACKAGE_NAME is installed"
    return 0
}

stop_services() {
    print_step "Stopping services and processes"
    
    # Stop any running processes
    pkill -f "pi-usb-safegate" || true
    pkill -f "cleanup_scheduler" || true
    
    # Stop systemd services if they exist
    if systemctl is-active --quiet pi-usb-safegate-cleanup.service; then
        systemctl stop pi-usb-safegate-cleanup.service
    fi
    
    if systemctl is-active --quiet pi-usb-safegate-cleanup.timer; then
        systemctl stop pi-usb-safegate-cleanup.timer
    fi
    
    print_success "Services stopped"
}

remove_package() {
    print_step "Removing package"
    
    if dpkg -l | grep -q "$PACKAGE_NAME"; then
        apt remove -y "$PACKAGE_NAME" || {
            print_error "Failed to remove package with apt"
            print_info "Trying dpkg removal..."
            dpkg --remove "$PACKAGE_NAME" || {
                print_error "Failed to remove package"
                exit 1
            }
        }
        print_success "Package removed"
    else
        print_info "Package not installed via dpkg"
    fi
}

remove_manual_installation() {
    print_step "Removing manual installation files"
    
    # Remove application files
    if [[ -d "/usr/share/pi-usb-safegate" ]]; then
        rm -rf /usr/share/pi-usb-safegate
        print_info "Removed application directory"
    fi
    
    # Remove binaries
    if [[ -f "/usr/bin/pi-usb-safegate" ]]; then
        rm -f /usr/bin/pi-usb-safegate
        print_info "Removed main binary"
    fi
    
    if [[ -f "/usr/bin/pi-usb-safegate-setup" ]]; then
        rm -f /usr/bin/pi-usb-safegate-setup
        print_info "Removed setup binary"
    fi
    
    # Remove desktop entry
    if [[ -f "/usr/share/applications/pi-usb-safegate.desktop" ]]; then
        rm -f /usr/share/applications/pi-usb-safegate.desktop
        print_info "Removed desktop entry"
    fi
    
    # Remove icon
    if [[ -f "/usr/share/pixmaps/pi-usb-safegate.svg" ]]; then
        rm -f /usr/share/pixmaps/pi-usb-safegate.svg
        print_info "Removed icon"
    fi
    
    # Remove udev rules
    if [[ -f "/etc/udev/rules.d/99-pi-usb-safegate.rules" ]]; then
        rm -f /etc/udev/rules.d/99-pi-usb-safegate.rules
        udevadm control --reload-rules || true
        print_info "Removed udev rules"
    fi
    
    # Remove systemd files
    if [[ -f "/etc/systemd/system/pi-usb-safegate-cleanup.service" ]]; then
        systemctl disable pi-usb-safegate-cleanup.service || true
        rm -f /etc/systemd/system/pi-usb-safegate-cleanup.service
        print_info "Removed systemd service"
    fi
    
    if [[ -f "/etc/systemd/system/pi-usb-safegate-cleanup.timer" ]]; then
        systemctl disable pi-usb-safegate-cleanup.timer || true
        rm -f /etc/systemd/system/pi-usb-safegate-cleanup.timer
        print_info "Removed systemd timer"
    fi
    
    # Reload systemd if needed
    if command -v systemctl >/dev/null 2>&1; then
        systemctl daemon-reload || true
    fi
    
    print_success "Manual installation files removed"
}

ask_remove_config() {
    echo
    print_warning "The following configuration and data will be preserved:"
    echo "  - Configuration files: /etc/pi-usb-safegate/"
    echo "  - Log files: /var/log/pi-usb-safegate/"
    echo "  - Cleanup schedule: /var/log/pi-usb-safegate/cleanup_schedule.json"
    echo
    
    read -p "Do you want to remove configuration and data files? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

remove_config_and_data() {
    print_step "Removing configuration and data files"
    
    # Remove configuration
    if [[ -d "/etc/pi-usb-safegate" ]]; then
        rm -rf /etc/pi-usb-safegate
        print_info "Removed configuration directory"
    fi
    
    # Remove logs
    if [[ -d "/var/log/pi-usb-safegate" ]]; then
        rm -rf /var/log/pi-usb-safegate
        print_info "Removed log directory"
    fi
    
    # Remove logrotate config
    if [[ -f "/etc/logrotate.d/pi-usb-safegate" ]]; then
        rm -f /etc/logrotate.d/pi-usb-safegate
        print_info "Removed logrotate configuration"
    fi
    
    print_success "Configuration and data files removed"
}

cleanup_system() {
    print_step "Cleaning up system"
    
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database /usr/share/applications || true
    fi
    
    # Clean package cache
    apt autoremove -y || true
    apt autoclean || true
    
    print_success "System cleanup completed"
}

main() {
    print_header
    
    check_root
    check_if_installed
    
    echo -e "${YELLOW}This will remove $APP_NAME from your system.${NC}"
    read -p "Are you sure you want to continue? (y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Uninstallation cancelled"
        exit 0
    fi
    
    stop_services
    remove_package
    remove_manual_installation
    
    if ask_remove_config; then
        remove_config_and_data
    fi
    
    cleanup_system
    
    echo
    echo -e "${GREEN}=================================================================================${NC}"
    echo -e "${GREEN}                        Uninstallation Complete!${NC}"
    echo -e "${GREEN}=================================================================================${NC}"
    echo
    echo -e "${BLUE}$APP_NAME has been removed from your system.${NC}"
    echo
    
    if [[ -d "/etc/pi-usb-safegate" ]] || [[ -d "/var/log/pi-usb-safegate" ]]; then
        echo -e "${YELLOW}Note: Some configuration and log files were preserved.${NC}"
        echo "To remove them completely, run this script again and choose 'y' when asked."
    fi
    
    echo
    echo -e "${BLUE}Thank you for using $APP_NAME!${NC}"
    echo
}

# Run main function
main "$@"