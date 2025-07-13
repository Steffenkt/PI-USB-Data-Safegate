# Makefile for PI USB Data Safegate

# Get version dynamically from Python module
PACKAGE_VERSION := $(shell python3 -c "import sys; sys.path.insert(0, 'src/pi_usb_safegate'); from version import get_version; print(get_version())")
PACKAGE_NAME := $(shell python3 -c "import sys; sys.path.insert(0, 'src/pi_usb_safegate'); from version import PACKAGE_NAME; print(PACKAGE_NAME)")
PACKAGE_ARCH := $(shell python3 -c "import sys; sys.path.insert(0, 'src/pi_usb_safegate'); from version import PACKAGE_ARCHITECTURE; print(PACKAGE_ARCHITECTURE)")
PACKAGE_FILE = $(PACKAGE_NAME)_$(PACKAGE_VERSION)_$(PACKAGE_ARCH).deb

BUILD_DIR = build
PACKAGE_DIR = packaging/debian-package

.PHONY: all clean build install test lint package help

# Default target
all: package

# Clean build directory
clean:
	@echo "Cleaning build directory..."
	rm -rf $(BUILD_DIR)
	rm -f $(PACKAGE_FILE)
	rm -f INSTALL.md

# Build the package
build: clean
	@echo "Building $(PACKAGE_NAME) package..."
	./scripts/build-package.sh

# Alias for build
package: build

# Install the package (for testing)
install: build
	@echo "Installing $(PACKAGE_NAME)..."
	sudo dpkg -i $(PACKAGE_FILE)
	sudo apt --fix-broken install -y

# Remove the package
uninstall:
	@echo "Removing $(PACKAGE_NAME)..."
	sudo apt remove -y $(PACKAGE_NAME)

# Purge the package and configuration
purge:
	@echo "Purging $(PACKAGE_NAME)..."
	sudo apt purge -y $(PACKAGE_NAME)

# Test the package
test: build
	@echo "Testing $(PACKAGE_NAME) package..."
	dpkg-deb --info $(PACKAGE_FILE)
	dpkg-deb --contents $(PACKAGE_FILE)

# Run lintian checks
lint: build
	@echo "Running lintian checks..."
	lintian $(PACKAGE_FILE) || true

# Check build dependencies
check-deps:
	@echo "Checking build dependencies..."
	@command -v dpkg-deb >/dev/null 2>&1 || { echo "Missing: dpkg-deb"; exit 1; }
	@command -v lintian >/dev/null 2>&1 || { echo "Missing: lintian (optional)"; }
	@command -v fakeroot >/dev/null 2>&1 || { echo "Missing: fakeroot"; exit 1; }
	@echo "All dependencies found"

# Install build dependencies
install-deps:
	@echo "Installing build dependencies..."
	sudo apt update
	sudo apt install -y dpkg-dev lintian fakeroot

# Development install (from source)
dev-install:
	@echo "Installing from source..."
	sudo ./scripts/install.sh

# Show package information
info:
	@echo "Package Information:"
	@echo "  Name: $(PACKAGE_NAME)"
	@echo "  Version: $(PACKAGE_VERSION)"
	@echo "  Architecture: $(PACKAGE_ARCH)"
	@echo "  Package file: $(PACKAGE_FILE)"

# Show version only
version:
	@echo $(PACKAGE_VERSION)

# Show package filename
filename:
	@echo $(PACKAGE_FILE)

# Help target
help:
	@echo "PI USB Data Safegate Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  all          - Build the Debian package (default)"
	@echo "  build        - Build the Debian package"
	@echo "  package      - Alias for build"
	@echo "  clean        - Clean build directory"
	@echo "  install      - Install the built package"
	@echo "  uninstall    - Remove the installed package"
	@echo "  purge        - Remove package and configuration"
	@echo "  test         - Test the built package"
	@echo "  lint         - Run lintian checks"
	@echo "  check-deps   - Check build dependencies"
	@echo "  install-deps - Install build dependencies"
	@echo "  dev-install  - Install from source using install.sh"
	@echo "  info         - Show package information"
	@echo "  version      - Show current version"
	@echo "  filename     - Show package filename"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Version management:"
	@echo "  python3 scripts/bump-version.py patch    # Bump patch version"
	@echo "  python3 scripts/bump-version.py minor    # Bump minor version"
	@echo "  python3 scripts/bump-version.py major    # Bump major version"
	@echo "  python3 tests/test-version.py            # Test version system"
	@echo ""
	@echo "Quick start:"
	@echo "  make install-deps  # Install build tools"
	@echo "  make build         # Build the package"
	@echo "  make install       # Install the package"