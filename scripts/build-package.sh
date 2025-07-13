#!/bin/bash

# Build script for PI USB Data Safegate Debian package

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get version from Python module
PACKAGE_VERSION=$(python3 -c "import sys; sys.path.insert(0, 'src/pi_usb_safegate'); from version import get_version; print(get_version())")
PACKAGE_NAME=$(python3 -c "import sys; sys.path.insert(0, 'src/pi_usb_safegate'); from version import PACKAGE_NAME; print(PACKAGE_NAME)")
PACKAGE_ARCH=$(python3 -c "import sys; sys.path.insert(0, 'src/pi_usb_safegate'); from version import PACKAGE_ARCHITECTURE; print(PACKAGE_ARCHITECTURE)")
PACKAGE_DIR="packaging/debian-package"
BUILD_DIR="/tmp/pi-usb-safegate-build-$$"

# Functions
print_step() {
    echo -e "${GREEN}[BUILD]${NC} $1"
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

check_dependencies() {
    print_step "Checking build dependencies"
    
    # Check for required tools
    local required_tools=("dpkg-deb" "fakeroot")
    local optional_tools=("lintian")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            print_error "Missing required tool: $tool"
            print_info "Install with: sudo apt install $tool"
            exit 1
        fi
    done
    
    for tool in "${optional_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            print_warning "Missing optional tool: $tool (linting will be skipped)"
        fi
    done
    
    print_success "All required build dependencies found"
}

clean_build() {
    print_step "Cleaning previous build"
    
    rm -rf "$BUILD_DIR"
    rm -f "${PACKAGE_NAME}_${PACKAGE_VERSION}_${PACKAGE_ARCH}.deb"
    rm -rf build/  # Also clean old build dir if it exists
    
    print_success "Build directory cleaned"
}

prepare_package() {
    print_step "Preparing package structure"
    
    # Create build directory
    mkdir -p "$BUILD_DIR"
    
    # Copy package structure
    cp -r "$PACKAGE_DIR"/* "$BUILD_DIR/"
    
    # Ensure application directory exists
    mkdir -p "$BUILD_DIR/usr/share/pi-usb-safegate/"
    
    # Copy application files
    cp -r src/pi_usb_safegate/* "$BUILD_DIR/usr/share/pi-usb-safegate/"
    
    # Copy and modify configuration
    cp config/config.ini "$BUILD_DIR/etc/pi-usb-safegate/config.ini.template"
    cp config/config.ini "$BUILD_DIR/etc/pi-usb-safegate/config.ini"
    
    # Copy systemd service file
    cp config/pi-usb-safegate.service "$BUILD_DIR/etc/systemd/system/"
    
    # Update main.py to use system config path
    sed -i 's|ConfigManager()|ConfigManager("/etc/pi-usb-safegate/config.ini")|g' "$BUILD_DIR/usr/share/pi-usb-safegate/main.py"
    
    # Set proper permissions (important for WSL)
    find "$BUILD_DIR" -type d -exec chmod 755 {} \;
    find "$BUILD_DIR" -type f -exec chmod 644 {} \;
    
    # Fix DEBIAN directory permissions specifically (dpkg-deb is strict about this)
    chmod 755 "$BUILD_DIR/DEBIAN"
    find "$BUILD_DIR/DEBIAN" -type f -exec chmod 644 {} \;
    
    # Make scripts executable
    chmod 755 "$BUILD_DIR/DEBIAN/postinst"
    chmod 755 "$BUILD_DIR/DEBIAN/prerm"
    chmod 755 "$BUILD_DIR/DEBIAN/postrm"
    chmod 755 "$BUILD_DIR/usr/bin/pi-usb-safegate"
    chmod 755 "$BUILD_DIR/usr/bin/pi-usb-safegate-setup"
    chmod 755 "$BUILD_DIR/usr/share/pi-usb-safegate/main.py"
    
    print_success "Package structure prepared"
}

calculate_size() {
    print_step "Calculating installed size"
    
    local size=$(du -sk "$BUILD_DIR" | cut -f1)
    
    # Update control file with calculated size and version
    sed -i "s/Version: .*/Version: $PACKAGE_VERSION/" "$BUILD_DIR/DEBIAN/control"
    sed -i "s/Installed-Size: .*/Installed-Size: $size/" "$BUILD_DIR/DEBIAN/control"
    
    print_info "Installed size: ${size}KB"
}

build_package() {
    print_step "Building Debian package"
    
    local package_file="${PACKAGE_NAME}_${PACKAGE_VERSION}_${PACKAGE_ARCH}.deb"
    
    # Build the package
    fakeroot dpkg-deb --build "$BUILD_DIR" "$package_file"
    
    # Clean up temp build directory
    rm -rf "$BUILD_DIR"
    
    if [[ -f "$package_file" ]]; then
        print_success "Package built successfully: $package_file"
        
        # Show package info
        local file_size=$(ls -lh "$package_file" | awk '{print $5}')
        print_info "Package size: $file_size"
        
        return 0
    else
        print_error "Package build failed"
        return 1
    fi
}

lint_package() {
    print_step "Running lintian checks"
    
    local package_file="${PACKAGE_NAME}_${PACKAGE_VERSION}_${PACKAGE_ARCH}.deb"
    
    if command -v lintian >/dev/null 2>&1; then
        lintian "$package_file" || {
            print_warning "Lintian found issues (this may be normal for some packages)"
        }
    else
        print_warning "Lintian not found, skipping checks"
    fi
}

test_package() {
    print_step "Testing package installation (dry run)"
    
    local package_file="${PACKAGE_NAME}_${PACKAGE_VERSION}_${PACKAGE_ARCH}.deb"
    
    # Test package info
    dpkg-deb --info "$package_file"
    
    echo
    print_info "Package contents:"
    dpkg-deb --contents "$package_file"
    
    print_success "Package tests completed"
}

create_installation_guide() {
    print_step "Creating installation guide"
    
    local package_file="${PACKAGE_NAME}_${PACKAGE_VERSION}_${PACKAGE_ARCH}.deb"
    
    cat > INSTALL.md << EOF
# PI USB Data Safegate Installation Guide

## Quick Installation

### Option 1: Using the Debian Package (Recommended)

1. Download the package file: \`$package_file\`

2. Install the package:
   \`\`\`bash
   sudo dpkg -i $package_file
   \`\`\`

3. If there are dependency issues, fix them:
   \`\`\`bash
   sudo apt --fix-broken install
   \`\`\`

4. Configure the application:
   \`\`\`bash
   sudo pi-usb-safegate-setup
   \`\`\`

5. Run the application:
   \`\`\`bash
   sudo pi-usb-safegate
   \`\`\`

### Option 2: Using the Install Script

1. Make the install script executable:
   \`\`\`bash
   chmod +x install.sh
   \`\`\`

2. Run the installer:
   \`\`\`bash
   sudo ./install.sh
   \`\`\`

## Post-Installation

- Configuration file: \`/etc/pi-usb-safegate/config.ini\`
- Log files: \`/var/log/pi-usb-safegate/\`
- Application files: \`/usr/share/pi-usb-safegate/\`

## Uninstallation

To remove the application:
\`\`\`bash
sudo apt remove pi-usb-safegate
\`\`\`

To remove all configuration files:
\`\`\`bash
sudo apt purge pi-usb-safegate
\`\`\`

## Troubleshooting

### Common Issues

1. **Permission denied**: Make sure to run with sudo
2. **Missing dependencies**: Run \`sudo apt --fix-broken install\`
3. **ClamAV not working**: Run \`sudo freshclam\` to update virus database

### Getting Help

Check the application logs at \`/var/log/pi-usb-safegate/safegate.log\`
EOF
    
    print_success "Installation guide created: INSTALL.md"
}

main() {
    echo -e "${BLUE}=================================================================================${NC}"
    echo -e "${BLUE}                    PI USB Data Safegate Package Builder v${PACKAGE_VERSION}${NC}"
    echo -e "${BLUE}=================================================================================${NC}"
    echo
    
    check_dependencies
    clean_build
    prepare_package
    calculate_size
    build_package
    lint_package
    test_package
    create_installation_guide
    
    echo
    echo -e "${GREEN}=================================================================================${NC}"
    echo -e "${GREEN}                           Build Complete!${NC}"
    echo -e "${GREEN}=================================================================================${NC}"
    echo
    echo -e "${BLUE}Package file:${NC} ${PACKAGE_NAME}_${PACKAGE_VERSION}_${PACKAGE_ARCH}.deb"
    echo -e "${BLUE}Installation guide:${NC} INSTALL.md"
    echo
    echo -e "${YELLOW}To install the package:${NC}"
    echo "  sudo dpkg -i ${PACKAGE_NAME}_${PACKAGE_VERSION}_${PACKAGE_ARCH}.deb"
    echo "  sudo apt --fix-broken install  # if needed"
    echo "  sudo pi-usb-safegate-setup     # configure"
    echo "  sudo pi-usb-safegate           # run"
    echo
}

# Run main function
main "$@"