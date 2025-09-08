#!/bin/bash

# PI USB Data Safegate - Automated Installation Script
# This script installs all dependencies and sets up the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Application info
APP_NAME="PI USB Data Safegate"
APP_VERSION="1.0.1"
APP_DIR="/usr/share/pi-usb-safegate"
BIN_DIR="/usr/bin"
CONFIG_DIR="/etc/pi-usb-safegate"
LOG_DIR="/var/log/pi-usb-safegate"

# Functions
print_header() {
    echo -e "${BLUE}=================================================================================${NC}"
    echo -e "${BLUE}                      $APP_NAME v$APP_VERSION Installer${NC}"
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
    
    # Create requirements.txt if it doesn't exist
    if [[ ! -f "requirements.txt" ]]; then
        cat > requirements.txt << 'EOF'
requests>=2.25.1
configparser>=5.0.0
pathlib>=1.0.1
EOF
    fi
    
    pip3 install -r requirements.txt || {
        print_error "Failed to install Python dependencies"
        exit 1
    }
    
    print_success "Python dependencies installed"
}

setup_clamav() {
    print_step "Setting up ClamAV antivirus"
    
    # Stop services if running
    systemctl stop clamav-freshclam || true
    systemctl stop clamav-daemon || true
    
    # Update virus database
    print_info "Updating ClamAV virus database (this may take a while)..."
    freshclam || {
        print_warning "ClamAV database update failed, but continuing..."
    }
    
    # Start services
    systemctl enable clamav-freshclam
    systemctl enable clamav-daemon
    systemctl start clamav-freshclam
    systemctl start clamav-daemon
    
    print_success "ClamAV configured and started"
}

create_directories() {
    print_step "Creating application directories"
    
    mkdir -p "$APP_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "/usr/share/applications"
    mkdir -p "/usr/share/pixmaps"
    
    print_success "Application directories created"
}

install_application() {
    print_step "Installing application files"
    
    # Copy main application
    cp -r . "$APP_DIR/"
    
    # Set proper permissions
    chown -R root:root "$APP_DIR"
    chmod 755 "$APP_DIR"
    find "$APP_DIR" -type f -name "*.py" -exec chmod 644 {} \;
    chmod 755 "$APP_DIR/main.py"
    
    # Create wrapper script
    cat > "$BIN_DIR/pi-usb-safegate" << 'EOF'
#!/bin/bash
# PI USB Data Safegate launcher script

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "This application requires root privileges to access USB devices."
    echo "Please run with: sudo pi-usb-safegate"
    exit 1
fi

# Change to application directory
cd /usr/share/pi-usb-safegate

# Run the application
python3 main.py "$@"
EOF
    
    chmod 755 "$BIN_DIR/pi-usb-safegate"
    
    print_success "Application files installed"
}

setup_configuration() {
    print_step "Setting up configuration"
    
    # Copy config template to system config directory
    cp config.ini "$CONFIG_DIR/config.ini.template"
    
    # Create default config if it doesn't exist
    if [[ ! -f "$CONFIG_DIR/config.ini" ]]; then
        cp config.ini "$CONFIG_DIR/config.ini"
    fi
    
    # Set proper permissions
    chown root:root "$CONFIG_DIR/config.ini"
    chmod 640 "$CONFIG_DIR/config.ini"
    
    # Update main.py to use system config
    sed -i "s|config.ini|$CONFIG_DIR/config.ini|g" "$APP_DIR/main.py"
    
    print_success "Configuration files setup"
}

create_desktop_entry() {
    print_step "Creating desktop entry"
    
    # Create icon (simple text-based icon)
    cat > "/usr/share/pixmaps/pi-usb-safegate.svg" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <rect width="64" height="64" fill="#2196F3" rx="8"/>
  <rect x="16" y="20" width="32" height="20" fill="#FFF" rx="2"/>
  <rect x="20" y="24" width="24" height="3" fill="#2196F3"/>
  <rect x="20" y="29" width="16" height="3" fill="#2196F3"/>
  <rect x="20" y="34" width="20" height="3" fill="#2196F3"/>
  <circle cx="32" cy="48" r="6" fill="#FFF"/>
  <path d="M32 44 L32 52 M28 48 L36 48" stroke="#2196F3" stroke-width="2" stroke-linecap="round"/>
</svg>
EOF
    
    # Create desktop entry
    cat > "/usr/share/applications/pi-usb-safegate.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=PI USB Data Safegate
Comment=Secure USB to cloud transfer with malware scanning
Exec=pkexec /usr/bin/pi-usb-safegate
Icon=pi-usb-safegate
Terminal=false
StartupNotify=true
Categories=System;Security;Utility;
Keywords=USB;Security;Malware;Cloud;Transfer;
EOF
    
    print_success "Desktop entry created"
}

setup_logging() {
    print_step "Setting up logging"
    
    # Create log directory with proper permissions
    chown root:root "$LOG_DIR"
    chmod 755 "$LOG_DIR"
    
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

setup_udev_rules() {
    print_step "Setting up USB device detection rules"
    
    cat > "/etc/udev/rules.d/99-pi-usb-safegate.rules" << 'EOF'
# USB storage device rules for PI USB Data Safegate
SUBSYSTEM=="block", KERNEL=="sd[a-z][0-9]", ACTION=="add", ENV{ID_FS_USAGE}=="filesystem", TAG+="systemd", ENV{SYSTEMD_WANTS}+="pi-usb-safegate-notify@%k.service"
EOF
    
    udevadm control --reload-rules
    
    print_success "USB device detection rules configured"
}

create_first_run_script() {
    print_step "Creating first-run configuration script"
    
    cat > "$BIN_DIR/pi-usb-safegate-setup" << 'EOF'
#!/bin/bash
# First-run configuration script for PI USB Data Safegate

CONFIG_FILE="/etc/pi-usb-safegate/config.ini"
TEMP_CONFIG="/tmp/pi-usb-safegate-config.tmp"

echo "================================================================================"
echo "                    PI USB Data Safegate - First Run Setup"
echo "================================================================================"
echo

if [[ $EUID -ne 0 ]]; then
    echo "This setup script must be run as root (use sudo)"
    exit 1
fi

echo "This script will help you configure PI USB Data Safegate for first use."
echo "You can also manually edit the configuration file at: $CONFIG_FILE"
echo

read -p "Would you like to configure the application now? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Configuration skipped. Run 'sudo pi-usb-safegate-setup' later to configure."
    exit 0
fi

# Copy current config to temp file
cp "$CONFIG_FILE" "$TEMP_CONFIG"

echo
echo "=== EMAIL CONFIGURATION ==="
read -p "SMTP Server (e.g., smtp.gmail.com): " smtp_server
read -p "SMTP Port (e.g., 587): " smtp_port
read -p "Email Username: " email_username
read -s -p "Email Password: " email_password
echo
read -p "Sender Name: " sender_name

# Update email configuration
sed -i "s|smtp_server = .*|smtp_server = $smtp_server|g" "$TEMP_CONFIG"
sed -i "s|smtp_port = .*|smtp_port = $smtp_port|g" "$TEMP_CONFIG"
sed -i "s|smtp_username = .*|smtp_username = $email_username|g" "$TEMP_CONFIG"
sed -i "s|smtp_password = .*|smtp_password = $email_password|g" "$TEMP_CONFIG"
sed -i "s|sender_name = .*|sender_name = $sender_name|g" "$TEMP_CONFIG"

echo
echo "=== CLOUD STORAGE CONFIGURATION ==="
echo "Select cloud storage provider:"
echo "1) Nextcloud"
echo "2) Dropbox"
read -p "Choice (1-2): " cloud_choice

if [[ $cloud_choice == "1" ]]; then
    sed -i "s|provider = .*|provider = nextcloud|g" "$TEMP_CONFIG"
    read -p "Nextcloud URL: " nextcloud_url
    read -p "Nextcloud Username: " nextcloud_username
    read -s -p "Nextcloud Password: " nextcloud_password
    echo
    read -p "Upload Path (e.g., /USB_Transfers): " upload_path
    
    sed -i "s|nextcloud_url = .*|nextcloud_url = $nextcloud_url|g" "$TEMP_CONFIG"
    sed -i "s|nextcloud_username = .*|nextcloud_username = $nextcloud_username|g" "$TEMP_CONFIG"
    sed -i "s|nextcloud_password = .*|nextcloud_password = $nextcloud_password|g" "$TEMP_CONFIG"
    sed -i "s|nextcloud_upload_path = .*|nextcloud_upload_path = $upload_path|g" "$TEMP_CONFIG"
    
elif [[ $cloud_choice == "2" ]]; then
    sed -i "s|provider = .*|provider = dropbox|g" "$TEMP_CONFIG"
    read -p "Dropbox Access Token: " dropbox_token
    sed -i "s|dropbox_access_token = .*|dropbox_access_token = $dropbox_token|g" "$TEMP_CONFIG"
fi

# Save configuration
cp "$TEMP_CONFIG" "$CONFIG_FILE"
rm "$TEMP_CONFIG"

echo
echo "Configuration saved successfully!"
echo "You can now run 'sudo pi-usb-safegate' to start the application."
echo "Or find it in your applications menu under 'PI USB Data Safegate'."
EOF
    
    chmod 755 "$BIN_DIR/pi-usb-safegate-setup"
    
    print_success "First-run configuration script created"
}

cleanup() {
    print_step "Cleaning up temporary files"
    
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
    create_desktop_entry
    setup_logging
    setup_udev_rules
    create_first_run_script
    cleanup
    
    echo
    echo -e "${GREEN}=================================================================================${NC}"
    echo -e "${GREEN}                        Installation Complete!${NC}"
    echo -e "${GREEN}=================================================================================${NC}"
    echo
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Run configuration setup: ${YELLOW}sudo pi-usb-safegate-setup${NC}"
    echo "2. Start the application: ${YELLOW}sudo pi-usb-safegate${NC}"
    echo "3. Or find it in your applications menu"
    echo
    echo -e "${BLUE}Configuration file location:${NC} $CONFIG_DIR/config.ini"
    echo -e "${BLUE}Log files location:${NC} $LOG_DIR/"
    echo
    echo -e "${YELLOW}Important:${NC} This application requires root privileges to access USB devices."
    echo
}

# Run main function
main "$@"