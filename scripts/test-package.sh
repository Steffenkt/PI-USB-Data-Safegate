#!/bin/bash

# Test script for PI USB Data Safegate package

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PACKAGE_NAME="pi-usb-safegate"
PACKAGE_VERSION="1.0.0"
PACKAGE_ARCH="all"
PACKAGE_FILE="${PACKAGE_NAME}_${PACKAGE_VERSION}_${PACKAGE_ARCH}.deb"

print_step() {
    echo -e "${GREEN}[TEST]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

test_package_structure() {
    print_step "Testing package structure"
    
    if [[ ! -f "$PACKAGE_FILE" ]]; then
        print_error "Package file not found: $PACKAGE_FILE"
        print_info "Run: ./build-package.sh to build the package"
        exit 1
    fi
    
    # Test package info
    print_info "Package information:"
    dpkg-deb --info "$PACKAGE_FILE"
    
    echo
    print_info "Package contents:"
    dpkg-deb --contents "$PACKAGE_FILE"
    
    print_success "Package structure test passed"
}

test_lintian() {
    print_step "Running lintian checks"
    
    if command -v lintian >/dev/null 2>&1; then
        lintian "$PACKAGE_FILE" || {
            print_error "Lintian found issues"
            return 1
        }
        print_success "Lintian checks passed"
    else
        print_info "Lintian not available, skipping checks"
    fi
}

test_dependencies() {
    print_step "Testing dependencies"
    
    # Extract control file
    dpkg-deb --control "$PACKAGE_FILE" /tmp/control-test
    
    if [[ -f "/tmp/control-test/control" ]]; then
        print_info "Dependencies listed in control file:"
        grep "Depends:" /tmp/control-test/control || true
        
        # Clean up
        rm -rf /tmp/control-test
        
        print_success "Dependencies test passed"
    else
        print_error "Could not extract control file"
        return 1
    fi
}

test_file_permissions() {
    print_step "Testing file permissions"
    
    # Extract package contents
    mkdir -p /tmp/package-test
    dpkg-deb --extract "$PACKAGE_FILE" /tmp/package-test
    
    # Check executable permissions
    local executables=(
        "/tmp/package-test/usr/bin/pi-usb-safegate"
        "/tmp/package-test/usr/bin/pi-usb-safegate-setup"
        "/tmp/package-test/usr/share/pi-usb-safegate/main.py"
    )
    
    for executable in "${executables[@]}"; do
        if [[ -f "$executable" ]]; then
            if [[ -x "$executable" ]]; then
                print_info "✓ $executable is executable"
            else
                print_error "✗ $executable is not executable"
                return 1
            fi
        else
            print_error "✗ $executable not found"
            return 1
        fi
    done
    
    # Check config file permissions
    if [[ -f "/tmp/package-test/etc/pi-usb-safegate/config.ini.template" ]]; then
        print_info "✓ Config template found"
    else
        print_error "✗ Config template not found"
        return 1
    fi
    
    # Clean up
    rm -rf /tmp/package-test
    
    print_success "File permissions test passed"
}

test_desktop_integration() {
    print_step "Testing desktop integration"
    
    # Extract package contents
    mkdir -p /tmp/desktop-test
    dpkg-deb --extract "$PACKAGE_FILE" /tmp/desktop-test
    
    # Check desktop entry
    if [[ -f "/tmp/desktop-test/usr/share/applications/pi-usb-safegate.desktop" ]]; then
        print_info "✓ Desktop entry found"
        
        # Validate desktop entry
        if command -v desktop-file-validate >/dev/null 2>&1; then
            desktop-file-validate "/tmp/desktop-test/usr/share/applications/pi-usb-safegate.desktop"
            print_info "✓ Desktop entry is valid"
        else
            print_info "desktop-file-validate not available, skipping validation"
        fi
    else
        print_error "✗ Desktop entry not found"
        return 1
    fi
    
    # Check icon
    if [[ -f "/tmp/desktop-test/usr/share/pixmaps/pi-usb-safegate.svg" ]]; then
        print_info "✓ Icon found"
    else
        print_error "✗ Icon not found"
        return 1
    fi
    
    # Clean up
    rm -rf /tmp/desktop-test
    
    print_success "Desktop integration test passed"
}

test_installation_simulation() {
    print_step "Simulating installation"
    
    # Create temporary directory for simulation
    mkdir -p /tmp/install-test
    
    # Extract package
    dpkg-deb --extract "$PACKAGE_FILE" /tmp/install-test
    
    # Check if all expected files are present
    local expected_files=(
        "/tmp/install-test/usr/share/pi-usb-safegate/main.py"
        "/tmp/install-test/usr/share/pi-usb-safegate/modules/__init__.py"
        "/tmp/install-test/usr/bin/pi-usb-safegate"
        "/tmp/install-test/usr/bin/pi-usb-safegate-setup"
        "/tmp/install-test/etc/pi-usb-safegate/config.ini.template"
        "/tmp/install-test/usr/share/applications/pi-usb-safegate.desktop"
    )
    
    for file in "${expected_files[@]}"; do
        if [[ -f "$file" ]]; then
            print_info "✓ $file"
        else
            print_error "✗ $file not found"
            return 1
        fi
    done
    
    # Clean up
    rm -rf /tmp/install-test
    
    print_success "Installation simulation passed"
}

main() {
    echo -e "${BLUE}=================================================================================${NC}"
    echo -e "${BLUE}                    PI USB Data Safegate Package Test${NC}"
    echo -e "${BLUE}=================================================================================${NC}"
    echo
    
    test_package_structure
    echo
    test_dependencies
    echo
    test_file_permissions
    echo
    test_desktop_integration
    echo
    test_installation_simulation
    echo
    test_lintian
    
    echo
    echo -e "${GREEN}=================================================================================${NC}"
    echo -e "${GREEN}                        All Tests Passed!${NC}"
    echo -e "${GREEN}=================================================================================${NC}"
    echo
    echo -e "${BLUE}Package is ready for installation:${NC}"
    echo "  sudo dpkg -i $PACKAGE_FILE"
    echo "  sudo apt --fix-broken install"
    echo "  sudo pi-usb-safegate-setup"
    echo
}

main "$@"