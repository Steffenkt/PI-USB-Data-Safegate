# Changelog

All notable changes to PI USB Data Safegate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation planning
- Future feature considerations

### Changed
- Ongoing improvements

## [1.0.1] - 2025-09-08

### Changed
- Migration von gksu zu pkexec / polkit (gksu entfernt – veraltet in aktuellen Debian/Raspberry Pi OS Releases)
- Debian Paket-Abhängigkeiten bereinigt: Entfernt `python3-pip`, `python3-dev`; hinzugefügt systemweite Python-Abhängigkeiten (`python3-requests`, `python3-pyudev`, `python3-magic`) für automatische Installation via APT
- Desktop-Start (`.desktop`) und Installationsskript auf `pkexec /usr/bin/pi-usb-safegate` umgestellt
- Post-Installationsskript: Entfernt pip basierte Modulinstallation, stattdessen Validierungs-Check der Module
- Control-Datei: Entfernt veraltete Abhängigkeit `gksu`, ersetzt durch `policykit-1`

### Added
- Polkit Policy Datei (`de.kasterdevelopment.pi-usb-safegate.policy`) für privilegierten GUI-Start

### Fixed
- Installationsfehler durch unerfüllbare gksu-Abhängigkeit
- Potentielle Offline-Installationsprobleme (kein spontaner pip Download mehr notwendig)

### Security
- Reduziert Angriffsfläche durch Entfernung von gksu und Nutzung aktueller PolicyKit Authentifizierung

## [1.0.0] - 2024-01-15

### Added
- **Headless Daemon Architecture**: Continuous background monitoring as systemd service
- **USB Device Detection**: Real-time USB drive monitoring using udev and pyudev
- **Nextcloud Integration**: Complete WebDAV and OCS API support for file upload and sharing
- **Malware Scanning**: ClamAV integration with virus detection and quarantine
- **Email Notifications**: Professional HTML email templates with download links
- **File Processing**: ZIP compression and integrity verification
- **Automatic Cleanup**: Configurable file deletion after specified time
- **Status Management**: Real-time service status tracking and IPC
- **Configuration Management**: Centralized INI-based configuration system
- **Systemd Integration**: Complete service management with auto-start
- **Package Management**: Debian package (.deb) with proper dependencies
- **Installation Scripts**: Automated installer with dependency management
- **Documentation**: Comprehensive guides for installation, usage, and troubleshooting

### Security
- **Multi-layer Security**: Input validation, malware scanning, encrypted transfers
- **Access Control**: Root privilege requirements for USB device access
- **Credential Protection**: Secure app password storage and handling
- **Network Security**: HTTPS enforcement for all cloud communications
- **File Isolation**: Infected file quarantine and safe processing

### Technical
- **Python 3.7+**: Modern Python implementation with type hints
- **Threading Architecture**: Concurrent processing with queue-based USB handling
- **Error Handling**: Comprehensive error recovery and logging
- **Resource Management**: Memory and CPU optimization for Raspberry Pi
- **API Integration**: RESTful Nextcloud API with proper authentication

### Documentation
- **Installation Guide**: Complete setup instructions for Raspberry Pi OS
- **Configuration Reference**: Detailed configuration options and examples
- **Usage Manual**: Step-by-step operating procedures
- **Architecture Documentation**: Technical design and component overview
- **Troubleshooting Guide**: Common issues and solutions
- **CI/CD Documentation**: Release and build process documentation

## [0.1.0] - 2024-01-10

### Added
- Initial project structure
- Basic concept validation
- Technology stack selection
- Requirements analysis

---

## Release Notes Template

### Version Categories

- **Major (X.0.0)**: Breaking changes, major new features, architecture changes
- **Minor (X.Y.0)**: New features, enhancements, backward-compatible changes
- **Patch (X.Y.Z)**: Bug fixes, security patches, minor improvements

### Change Categories

- **Added**: New features and capabilities
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements and patches

### Development Guidelines

#### Adding Entries

When making changes, add entries under the `[Unreleased]` section:

```markdown
## [Unreleased]

### Added
- New USB drive auto-mount feature
- Support for exFAT file systems

### Fixed
- Email delivery timeout issues
- Memory leak in file processing
```

#### Release Process

1. Move entries from `[Unreleased]` to new version section
2. Update version in `version.py`
3. Commit changes
4. Trigger GitHub Actions release workflow

#### Example Entry Format

```markdown
## [1.1.0] - 2024-02-15

### Added
- Support for multiple cloud providers
- Advanced file filtering options
- Real-time progress notifications

### Changed
- Improved email template design
- Enhanced error reporting

### Fixed
- USB detection on newer kernels
- Configuration file validation

### Security
- Updated ClamAV integration
- Enhanced credential encryption
```

### Breaking Changes

For major version releases, document breaking changes:

```markdown
## [2.0.0] - 2024-06-01

### ⚠️ BREAKING CHANGES

- Configuration file format changed
- Minimum Python version now 3.9
- Service name changed from `usb-safegate` to `pi-usb-safegate`

### Migration Guide

1. **Configuration**: Use migration script: `python3 migrate-config.py`
2. **Service**: Restart service after update
3. **Dependencies**: Update Python environment
```

### Links Reference

Compare versions and view detailed changes:

- [Unreleased]: https://github.com/Steffenkt/PI-USB-Data-Safegate/compare/v1.0.1...HEAD
- [1.0.1]: https://github.com/Steffenkt/PI-USB-Data-Safegate/compare/v1.0.0...v1.0.1
- [1.0.0]: https://github.com/Steffenkt/PI-USB-Data-Safegate/compare/v0.1.0...v1.0.0
- [0.1.0]: https://github.com/Steffenkt/PI-USB-Data-Safegate/releases/tag/v0.1.0