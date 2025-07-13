# CI/CD and Release Management

This document provides comprehensive information about the Continuous Integration/Continuous Deployment (CI/CD) system and release management for PI USB Data Safegate.

## Overview

The project uses a modern CI/CD pipeline built with GitHub Actions to:
- Automatically build Debian packages
- Create versioned releases
- Upload release assets
- Maintain release consistency
- Provide reproducible builds

## Versioning System

### Semantic Versioning

The project follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes
- **PRERELEASE**: Optional pre-release identifier (alpha, beta, rc1)
- **BUILD**: Optional build metadata

### Version Management

#### Centralized Version Control

All version information is managed in `version.py`:

```python
# Application Version (Semantic Versioning)
__version__ = "1.0.0"

# Version metadata
VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'patch': 0,
    'release': 'stable',
    'build': None
}
```

#### Version Display

The version is automatically displayed in:
- Application GUI title bar
- Log file headers
- Service startup messages
- Package filenames
- Release assets

#### Dynamic Version Extraction

Build scripts automatically extract version information:

```bash
# Get version from Python module
PACKAGE_VERSION=$(python3 -c "from version import get_version; print(get_version())")
PACKAGE_NAME=$(python3 -c "from version import PACKAGE_NAME; print(PACKAGE_NAME)")
```

## Release Process

### Manual Release Workflow

The release process is triggered manually through GitHub Actions to ensure quality control and intentional releases.

#### Step 1: Version Bump

Update the version using the bump script:

```bash
# Patch release (1.0.0 → 1.0.1)
python3 bump-version.py patch

# Minor release (1.0.0 → 1.1.0)
python3 bump-version.py minor

# Major release (1.0.0 → 2.0.0)
python3 bump-version.py major

# Pre-release (1.0.0 → 1.1.0-beta)
python3 bump-version.py minor --prerelease beta

# Dry run (preview changes)
python3 bump-version.py patch --dry-run
```

#### Step 2: Commit Version Changes

```bash
# Review changes
git diff

# Commit version bump
git add version.py CHANGELOG.md
git commit -m "Bump version to 1.0.1"
git push origin main
```

#### Step 3: Trigger Release Workflow

1. Go to GitHub Actions tab
2. Select "Build and Release PI USB Data Safegate"
3. Click "Run workflow"
4. Choose release type (patch/minor/major)
5. Configure release options:
   - **Pre-release**: Mark as pre-release
   - **Draft**: Create as draft for review

#### Step 4: Review and Publish

1. Verify build completed successfully
2. Review generated release notes
3. Test the package if needed
4. Publish draft release (if created as draft)

### Automated Process Details

The GitHub Actions workflow performs these steps:

#### 1. Validation Job
- Validates version format
- Checks for version conflicts
- Verifies dependencies
- Extracts build metadata

#### 2. Build Job
- Sets up build environment
- Installs dependencies
- Builds Debian package
- Validates package structure
- Runs lintian checks
- Generates checksums

#### 3. Release Job
- Creates Git tag
- Generates release notes
- Creates GitHub release
- Uploads package assets
- Provides installation instructions

#### 4. Notification Job
- Reports workflow status
- Provides build summary
- Flags any issues

## GitHub Actions Workflow

### Workflow File

Location: `.github/workflows/build-release.yml`

### Trigger Configuration

```yaml
on:
  workflow_dispatch:
    inputs:
      release_type:
        description: 'Type of release'
        required: true
        default: 'patch'
        type: choice
        options:
          - patch
          - minor
          - major
      prerelease:
        description: 'Mark as pre-release'
        required: false
        default: false
        type: boolean
      draft:
        description: 'Create as draft release'
        required: false
        default: false
        type: boolean
```

### Environment Variables

- `PACKAGE_NAME`: pi-usb-safegate
- `GITHUB_TOKEN`: Automatically provided by GitHub

### Required Secrets

No additional secrets required - uses built-in `GITHUB_TOKEN`.

### Job Dependencies

```
validate → build → release → notify
```

## Local Development

### Building Packages Locally

#### Using Make

```bash
# Show current version
make version

# Show package filename
make filename

# Build package
make build

# Install package locally
make install

# Run tests
make test
```

#### Using Build Script

```bash
# Build package
./build-package.sh

# Test package
./test-package.sh
```

### Version Utilities

#### Check Current Version

```bash
# Show version only
python3 version.py version

# Show detailed info
python3 version.py info

# Show package filename
python3 version.py package

# Show build information
python3 version.py build-info
```

#### Version Validation

```bash
# Check version consistency
python3 bump-version.py --current

# Validate version format
python3 -c "from version import parse_version; parse_version('1.0.0')"
```

## Package Management

### Package Structure

```
pi-usb-safegate_1.0.0_all.deb
├── DEBIAN/
│   ├── control                 # Package metadata
│   ├── postinst               # Post-installation script
│   ├── prerm                  # Pre-removal script
│   └── postrm                 # Post-removal script
├── usr/
│   ├── bin/
│   │   ├── pi-usb-safegate           # Main executable
│   │   └── pi-usb-safegate-setup     # Configuration wizard
│   └── share/
│       └── pi-usb-safegate/
│           ├── daemon.py             # Main daemon
│           ├── main.py               # GUI application
│           ├── version.py            # Version info
│           ├── modules/              # Application modules
│           └── requirements.txt      # Python dependencies
├── etc/
│   ├── pi-usb-safegate/
│   │   └── config.ini.template       # Configuration template
│   └── systemd/system/
│       └── pi-usb-safegate.service   # Service definition
└── usr/share/applications/
    └── pi-usb-safegate.desktop       # Desktop entry
```

### Package Metadata

The `control` file includes:

```
Package: pi-usb-safegate
Version: 1.0.0                    # Automatically updated
Architecture: all
Depends: python3, clamav, ...     # System dependencies
Description: Secure USB to cloud transfer with malware scanning
```

### Asset Files

Each release includes:

- **Package**: `pi-usb-safegate_1.0.0_all.deb`
- **SHA256**: `pi-usb-safegate_1.0.0_all.deb.sha256`
- **MD5**: `pi-usb-safegate_1.0.0_all.deb.md5`

## Quality Assurance

### Automated Checks

#### Package Validation
- Package structure verification
- File permissions check
- Service file validation
- Configuration template verification

#### Code Quality
- Lintian package checks
- Python syntax validation
- Import dependency verification

#### Version Consistency
- Version format validation
- Release tag uniqueness
- Version synchronization across files

### Testing Procedures

#### Pre-Release Testing

```bash
# Test version utilities
python3 version.py info
python3 bump-version.py --current

# Test build process
make clean && make build

# Test package contents
dpkg-deb --contents pi-usb-safegate_*.deb

# Test package installation (in VM/container)
sudo dpkg -i pi-usb-safegate_*.deb
sudo apt --fix-broken install
```

#### Integration Testing

1. **Build Test**: Verify package builds successfully
2. **Installation Test**: Test package installation process
3. **Service Test**: Verify systemd service starts correctly
4. **Configuration Test**: Test configuration wizard
5. **Functionality Test**: Basic application functionality

## Release Asset Management

### Automatic Asset Generation

Each release automatically generates:

1. **Debian Package**: Complete installation package
2. **Checksums**: SHA256 and MD5 verification files
3. **Release Notes**: Formatted installation instructions
4. **Git Tag**: Version tag for source code reference

### Asset Verification

Users can verify package integrity:

```bash
# Download assets
wget https://github.com/USER/REPO/releases/download/v1.0.0/pi-usb-safegate_1.0.0_all.deb
wget https://github.com/USER/REPO/releases/download/v1.0.0/pi-usb-safegate_1.0.0_all.deb.sha256

# Verify integrity
sha256sum -c pi-usb-safegate_1.0.0_all.deb.sha256
```

## Troubleshooting

### Common Issues

#### Version Mismatch
```bash
# Check version consistency
python3 bump-version.py --current
make version
```

#### Build Failures
```bash
# Check build environment
python3 version.py build-info
make check-deps

# Test build locally
make clean && make build
```

#### Workflow Failures
1. Check GitHub Actions logs
2. Verify version format
3. Check for duplicate releases
4. Validate repository permissions

### Debug Commands

```bash
# Show detailed version info
python3 version.py build-info | jq .

# Test package build
./build-package.sh 2>&1 | tee build.log

# Validate package
lintian pi-usb-safegate_*.deb

# Test version extraction
python3 -c "from version import *; print(get_build_info())"
```

## Best Practices

### Version Management

1. **Follow Semantic Versioning**: Use appropriate version increments
2. **Update Changelog**: Document all changes in CHANGELOG.md
3. **Test Before Release**: Always test locally before triggering workflow
4. **Review Releases**: Use draft releases for review when needed

### Release Management

1. **Prepare Release Notes**: Update CHANGELOG.md before version bump
2. **Coordinate Releases**: Communicate with team before major releases
3. **Monitor Builds**: Watch GitHub Actions for build status
4. **Verify Assets**: Test release packages after creation

### Quality Control

1. **Consistent Versioning**: Use bump script for version changes
2. **Automated Testing**: Rely on CI/CD for validation
3. **Documentation**: Keep documentation current with releases
4. **Rollback Plan**: Know how to revert problematic releases

## Integration with Development Workflow

### Branching Strategy

```
main ← feature branches
  ↓
release workflow (manual trigger)
  ↓
GitHub Release
```

### Development Cycle

1. **Feature Development**: Work in feature branches
2. **Merge to Main**: Use pull requests for code review
3. **Version Bump**: Update version when ready for release
4. **Trigger Release**: Manual workflow trigger
5. **Validate Release**: Test and verify release assets

### Hotfix Process

For urgent fixes:

1. Create hotfix branch from main
2. Implement fix
3. Bump patch version
4. Trigger patch release
5. Verify fix deployment

## Maintenance

### Regular Tasks

#### Monthly
- Review and update dependencies
- Check for security updates
- Validate build environment

#### Per Release
- Update CHANGELOG.md
- Test package installation
- Verify documentation accuracy
- Check asset integrity

#### Annually
- Review versioning strategy
- Update CI/CD pipeline
- Audit release process
- Update documentation

### Monitoring

#### Metrics to Track
- Build success rate
- Release frequency
- Package download counts
- Issue reports post-release

#### Alerts
- Failed builds
- Version conflicts
- Security vulnerabilities
- Dependency updates

This CI/CD system provides a robust, automated, and reproducible release process that ensures high-quality packages while maintaining development velocity and release confidence.