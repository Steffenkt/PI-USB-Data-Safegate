#!/bin/bash

# Secure Nextcloud USB Uploader - Daemon Installation Script
# Installs the headless daemon version with all dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Application info
APP_NAME="Secure Nextcloud USB Uploader"
APP_VERSION="2.0.0"
SERVICE_NAME="pi-usb-safegate"
APP_DIR="/usr/share/pi-usb-safegate"
BIN_DIR="/usr/bin"
CONFIG_DIR="/etc/pi-usb-safegate"
LOG_DIR="/var/log/pi-usb-safegate"
RUN_DIR="/var/run/pi-usb-safegate"

print_header() {
    echo -e "${BLUE}=================================================================================${NC}"
    echo -e "${BLUE}                $APP_NAME v$APP_VERSION Installer${NC}"
    echo -e "${BLUE}                     Headless Daemon Edition${NC}"
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

check_os() {
    if [[ ! -f /etc/debian_version ]]; then
        print_error "This installer is designed for Debian-based systems (including Raspberry Pi OS)"
        exit 1
    fi
    
    print_info "Detected Debian-based system"
    
    if [[ -f /etc/rpi-issue ]]; then
        print_info "Raspberry Pi OS detected"
    fi
}

update_system() {
    print_step "Updating system package lists"
    apt update -qq || {
        print_error "Failed to update package lists"
        exit 1
    }
    print_success "System package lists updated"
}

install_system_dependencies() {
    print_step "Installing system dependencies"
    
    local packages=(
        "python3"
        "python3-pip"
        "python3-tk"
        "python3-dev"
        "clamav"
        "clamav-daemon"
        "clamav-freshclam"
        "udev"
        "mount"
        "util-linux"
        "curl"
        "wget"
        "libmagic1"
        "libmagic-dev"
        "file"
    )
    
    print_info "Installing packages: ${packages[*]}"
    
    DEBIAN_FRONTEND=noninteractive apt install -y "${packages[@]}" || {
        print_error "Failed to install system dependencies"
        exit 1
    }
    
    print_success "System dependencies installed"
}

install_python_dependencies() {
    print_step "Installing Python dependencies"
    
    # Upgrade pip first
    python3 -m pip install --upgrade pip
    
    # Install from requirements.txt
    if [[ -f "requirements.txt" ]]; then
        pip3 install -r requirements.txt || {
            print_error "Failed to install Python dependencies from requirements.txt"
            exit 1
        }
    else
        # Install individual packages
        pip3 install requests>=2.25.1 configparser>=5.0.0 pathlib>=1.0.1 || {
            print_error "Failed to install Python dependencies"
            exit 1
        }
        
        # Install optional dependencies
        pip3 install pyudev>=0.23.2 || print_warning "pyudev not installed - will use polling method"
        pip3 install python-magic>=0.4.24 || print_warning "python-magic not installed"
        pip3 install clamd>=1.0.2 || print_warning "clamd not installed"
    fi
    
    print_success "Python dependencies installed"
}

setup_clamav() {
    print_step "Setting up ClamAV antivirus"
    
    # Stop services if running
    systemctl stop clamav-freshclam || true
    systemctl stop clamav-daemon || true
    
    # Update virus database
    print_info "Updating ClamAV virus database (this may take several minutes)..."
    timeout 600 freshclam || {
        print_warning "ClamAV database update failed or timed out, but continuing..."
    }
    
    # Start and enable services
    systemctl enable clamav-freshclam
    systemctl enable clamav-daemon
    systemctl start clamav-freshclam
    
    # Wait for freshclam to complete if running
    sleep 5
    
    systemctl start clamav-daemon
    
    # Wait for daemon to start
    sleep 3
    
    if systemctl is-active --quiet clamav-daemon; then
        print_success "ClamAV configured and started"
    else
        print_warning "ClamAV daemon may not be running properly"
    fi
}

create_directories() {
    print_step "Creating application directories"
    
    mkdir -p "$APP_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$RUN_DIR"
    mkdir -p "/usr/share/applications"
    mkdir -p "/usr/share/pixmaps"
    
    # Set proper permissions
    chown root:root "$CONFIG_DIR" "$LOG_DIR" "$RUN_DIR"
    chmod 755 "$CONFIG_DIR" "$LOG_DIR" "$RUN_DIR"
    
    print_success "Application directories created"
}

install_application() {
    print_step "Installing application files"
    
    # Copy application files
    cp -r daemon.py modules/ requirements.txt "$APP_DIR/"
    
    # Copy documentation
    if [[ -d "_docs" ]]; then
        cp -r _docs "$APP_DIR/docs"
    fi
    
    # Set proper permissions
    chown -R root:root "$APP_DIR"
    chmod 755 "$APP_DIR"
    find "$APP_DIR" -type f -name "*.py" -exec chmod 644 {} \;
    chmod 755 "$APP_DIR/daemon.py"
    
    # Create daemon control script
    cp daemon-control.sh "$BIN_DIR/pi-usb-safegate-control"
    chmod 755 "$BIN_DIR/pi-usb-safegate-control"
    
    # Create simple wrapper script
    cat > "$BIN_DIR/pi-usb-safegate" << 'EOF'
#!/bin/bash
# PI USB Safegate daemon wrapper

if [[ $EUID -ne 0 ]]; then
    echo "This application requires root privileges."
    echo "Please run with: sudo pi-usb-safegate [command]"
    exit 1
fi

cd /usr/share/pi-usb-safegate
exec python3 daemon.py "$@"
EOF
    
    chmod 755 "$BIN_DIR/pi-usb-safegate"
    
    print_success "Application files installed"
}

setup_configuration() {
    print_step "Setting up configuration"
    
    # Copy config template
    cp config.ini "$CONFIG_DIR/config.ini.template"
    
    # Create default config if it doesn't exist
    if [[ ! -f "$CONFIG_DIR/config.ini" ]]; then
        cp config.ini "$CONFIG_DIR/config.ini"
    fi
    
    # Set proper permissions
    chown root:root "$CONFIG_DIR/config.ini"
    chmod 640 "$CONFIG_DIR/config.ini"
    
    print_success "Configuration files setup"
}

install_systemd_service() {
    print_step "Installing systemd service"
    
    # Copy service file
    cp pi-usb-safegate.service /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable service (but don't start yet)
    systemctl enable pi-usb-safegate
    
    print_success "Systemd service installed and enabled"
}

setup_udev_rules() {
    print_step "Setting up USB device detection rules"
    
    cat > "/etc/udev/rules.d/99-pi-usb-safegate.rules" << 'EOF'
# USB storage device rules for PI USB Data Safegate
SUBSYSTEM=="block", KERNEL=="sd[a-z][0-9]", ACTION=="add", ENV{ID_FS_USAGE}=="filesystem", TAG+="systemd"
SUBSYSTEM=="block", KERNEL=="sd[a-z][0-9]", ACTION=="remove", TAG+="systemd"
EOF
    
    # Reload udev rules
    udevadm control --reload-rules
    udevadm trigger
    
    print_success "USB device detection rules configured"
}

setup_logging() {
    print_step "Setting up logging"
    
    # Create logrotate configuration
    cat > "/etc/logrotate.d/pi-usb-safegate" << EOF
$LOG_DIR/*.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
    
    print_success "Logging configured"
}

create_configuration_wizard() {
    print_step "Creating configuration wizard"
    
    cat > "$BIN_DIR/pi-usb-safegate-setup" << 'EOF'
#!/bin/bash
# Configuration wizard for PI USB Data Safegate

CONFIG_FILE="/etc/pi-usb-safegate/config.ini"

echo "================================================================="
echo "     Secure Nextcloud USB Uploader - Configuration Setup"
echo "================================================================="
echo

if [[ $EUID -ne 0 ]]; then
    echo "This setup script must be run as root (use sudo)"
    exit 1
fi

echo "This wizard will help you configure the Secure Nextcloud USB Uploader."
echo "Press Enter to continue or Ctrl+C to exit..."
read

# Backup existing config
if [[ -f "$CONFIG_FILE" ]]; then
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

echo
echo "=== NEXTCLOUD CONFIGURATION ==="
read -p "Nextcloud Server URL (https://your-nextcloud.com): " nextcloud_url
read -p "Nextcloud Username: " nextcloud_username
read -s -p "Nextcloud App Password: " nextcloud_password
echo
read -p "Upload Directory (e.g., /USB_Transfers): " upload_path

echo
echo "=== EMAIL CONFIGURATION ==="
read -p "SMTP Server (e.g., smtp.gmail.com): " smtp_server
read -p "SMTP Port (e.g., 587): " smtp_port
read -p "Email Username: " email_username
read -s -p "Email Password: " email_password
echo
read -p "Sender Name (e.g., PI USB Safegate): " sender_name

# Update configuration file
python3 << PYTHON_EOF
import configparser

config = configparser.ConfigParser()
config.read('$CONFIG_FILE')

# Update Nextcloud settings
if not config.has_section('NEXTCLOUD'):
    config.add_section('NEXTCLOUD')
config.set('NEXTCLOUD', 'url', '$nextcloud_url')
config.set('NEXTCLOUD', 'username', '$nextcloud_username')
config.set('NEXTCLOUD', 'password', '$nextcloud_password')
config.set('NEXTCLOUD', 'upload_path', '$upload_path')

# Update email settings
if not config.has_section('EMAIL'):
    config.add_section('EMAIL')
config.set('EMAIL', 'smtp_server', '$smtp_server')
config.set('EMAIL', 'smtp_port', '$smtp_port')
config.set('EMAIL', 'smtp_username', '$email_username')
config.set('EMAIL', 'smtp_password', '$email_password')
config.set('EMAIL', 'sender_name', '$sender_name')

# Save configuration
with open('$CONFIG_FILE', 'w') as f:
    config.write(f)

print("Configuration saved successfully!")
PYTHON_EOF

echo
echo "Configuration completed!"
echo
echo "Next steps:"
echo "1. Start the service: sudo systemctl start pi-usb-safegate"
echo "2. Check status: sudo systemctl status pi-usb-safegate"
echo "3. View logs: sudo journalctl -u pi-usb-safegate -f"
echo
echo "Insert a USB drive to test the system!"
EOF
    
    chmod 755 "$BIN_DIR/pi-usb-safegate-setup"
    
    print_success "Configuration wizard created"
}

run_tests() {
    print_step "Running system tests"
    
    # Test ClamAV
    if systemctl is-active --quiet clamav-daemon; then
        print_info "✓ ClamAV daemon is running"
    else
        print_warning "✗ ClamAV daemon is not running"
    fi
    
    # Test Python dependencies
    python3 -c "import requests; print('✓ requests module available')" 2>/dev/null || print_warning "✗ requests module not available"
    python3 -c "import configparser; print('✓ configparser module available')" 2>/dev/null || print_warning "✗ configparser module not available"
    
    # Test daemon script
    if [[ -f "$APP_DIR/daemon.py" ]]; then
        print_info "✓ Daemon script installed"
    else
        print_warning "✗ Daemon script not found"
    fi
    
    print_success "System tests completed"
}

cleanup() {
    print_step "Cleaning up installation files"
    
    # Remove any temporary files
    rm -f /tmp/pi-usb-safegate-*
    
    # Clean package cache
    apt autoremove -y
    apt autoclean
    
    print_success "Cleanup completed"
}

main() {
    print_header
    
    check_root
    check_os
    update_system
    install_system_dependencies
    install_python_dependencies
    setup_clamav
    create_directories
    install_application
    setup_configuration
    install_systemd_service
    setup_udev_rules
    setup_logging
    create_configuration_wizard
    run_tests
    cleanup
    
    echo
    echo -e "${GREEN}=================================================================================${NC}"
    echo -e "${GREEN}                        Installation Complete!${NC}"
    echo -e "${GREEN}=================================================================================${NC}"
    echo
    echo -e "${BLUE}Secure Nextcloud USB Uploader has been installed successfully.${NC}"
    echo
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Configure the application: ${YELLOW}sudo pi-usb-safegate-setup${NC}"
    echo "2. Start the service: ${YELLOW}sudo systemctl start pi-usb-safegate${NC}"
    echo "3. Check service status: ${YELLOW}sudo systemctl status pi-usb-safegate${NC}"
    echo "4. View real-time logs: ${YELLOW}sudo journalctl -u pi-usb-safegate -f${NC}"
    echo
    echo -e "${BLUE}Service management:${NC}"
    echo "• Control service: ${YELLOW}sudo pi-usb-safegate-control [start|stop|status|logs]${NC}"
    echo "• Configuration file: ${YELLOW}/etc/pi-usb-safegate/config.ini${NC}"
    echo "• Log files: ${YELLOW}/var/log/pi-usb-safegate/${NC}"
    echo
    echo -e "${BLUE}Documentation:${NC}"
    echo "• Complete docs: ${YELLOW}/usr/share/pi-usb-safegate/docs/${NC}"
    echo "• README: ${YELLOW}/usr/share/pi-usb-safegate/docs/README.md${NC}"
    echo "• Configuration: ${YELLOW}/usr/share/pi-usb-safegate/docs/CONFIG.md${NC}"
    echo "• Usage guide: ${YELLOW}/usr/share/pi-usb-safegate/docs/USAGE.md${NC}"
    echo "• Troubleshooting: ${YELLOW}/usr/share/pi-usb-safegate/docs/TROUBLESHOOTING.md${NC}"
    echo
    echo -e "${GREEN}The service will automatically start monitoring for USB drives after configuration.${NC}"
    echo -e "${GREEN}Insert a USB drive to test the system!${NC}"
    echo
}

# Run main function
main "$@"