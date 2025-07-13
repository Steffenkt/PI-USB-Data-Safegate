# Architecture Documentation

This document describes the technical architecture, design patterns, and technology stack of the Secure Nextcloud USB Uploader.

## Overview

The Secure Nextcloud USB Uploader is designed as a modular, event-driven daemon service that provides secure, automated file transfer from USB drives to Nextcloud cloud storage. The architecture emphasizes security, reliability, and maintainability.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    System Architecture                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌──────────────────────────────┐   │
│  │  USB Devices    │    │       Raspberry Pi           │   │
│  │                 │    │                              │   │
│  │  ┌─────────────┐│    │  ┌─────────────────────────┐ │   │
│  │  │ Flash Drive ││◄───┤  │    Main Daemon Service  │ │   │
│  │  └─────────────┘│    │  │                         │ │   │
│  │                 │    │  │  ┌─────────────────────┐│ │   │
│  │  ┌─────────────┐│    │  │  │   USB Monitor       ││ │   │
│  │  │   SD Card   ││◄───┤  │  └─────────────────────┘│ │   │
│  │  └─────────────┘│    │  │                         │ │   │
│  │                 │    │  │  ┌─────────────────────┐│ │   │
│  │  ┌─────────────┐│    │  │  │ Malware Scanner     ││ │   │
│  │  │  USB HDD    ││◄───┤  │  └─────────────────────┘│ │   │
│  │  └─────────────┘│    │  │                         │ │   │
│  └─────────────────┘    │  │  ┌─────────────────────┐│ │   │
│                         │  │  │  File Processor     ││ │   │
│                         │  │  └─────────────────────┘│ │   │
│                         │  │                         │ │   │
│                         │  │  ┌─────────────────────┐│ │   │
│                         │  │  │ Nextcloud Uploader  ││ │   │
│                         │  │  └─────────────────────┘│ │   │
│                         │  │                         │ │   │
│                         │  │  ┌─────────────────────┐│ │   │
│                         │  │  │  Email Notifier     ││ │   │
│                         │  │  └─────────────────────┘│ │   │
│                         │  └─────────────────────────┘ │   │
│                         └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐         ┌─────────────────────────┐   │
│  │   Nextcloud     │         │     Email Server        │   │
│  │    Server       │         │                         │   │
│  │                 │         │  ┌─────────────────────┐│   │
│  │  WebDAV API     │◄────────┼──┤      SMTP          ││   │
│  │  OCS API        │         │  │                     ││   │
│  │  File Storage   │         │  │   TLS/SSL           ││   │
│  │  Public Shares  │         │  │   Authentication    ││   │
│  └─────────────────┘         │  └─────────────────────┘│   │
│                              └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Daemon Process                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                Main Service Controller                       │ │
│  │                                                             │ │
│  │  • Event Loop Management                                   │ │
│  │  • Component Coordination                                  │ │
│  │  • Error Handling & Recovery                               │ │
│  │  • Signal Handling                                         │ │
│  │  • Resource Management                                     │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────────┐│
│  │   USB Monitor   │  │ Malware Scanner │  │   File Processor   ││
│  │                 │  │                 │  │                    ││
│  │ • udev Events   │  │ • ClamAV Engine │  │ • ZIP Creation     ││
│  │ • Device Info   │  │ • Threat Detection│ │ • File Filtering  ││
│  │ • Mount Points  │  │ • Quarantine    │  │ • Compression     ││
│  └─────────────────┘  └─────────────────┘  └────────────────────┘│
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────────┐│
│  │Nextcloud Upload │  │ Email Notifier  │  │  Status Manager    ││
│  │                 │  │                 │  │                    ││
│  │ • WebDAV API    │  │ • SMTP Client   │  │ • State Tracking   ││
│  │ • File Upload   │  │ • HTML Templates│  │ • IPC             ││
│  │ • Share Links   │  │ • Delivery      │  │ • Persistence     ││
│  └─────────────────┘  └─────────────────┘  └────────────────────┘│
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────────┐│
│  │Config Manager   │  │Cleanup Scheduler│  │   GUI Components   ││
│  │                 │  │                 │  │                    ││
│  │ • INI Parsing   │  │ • Timed Deletion│  │ • Email Input      ││
│  │ • Validation    │  │ • Schedule DB   │  │ • Malware Warning  ││
│  │ • Defaults      │  │ • Background Job│  │ • Status Display   ││
│  └─────────────────┘  └─────────────────┘  └────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Main Daemon Service (`daemon.py`)

**Purpose**: Central orchestrator and event loop manager

**Responsibilities**:
- Service lifecycle management (start/stop/restart)
- Component initialization and coordination
- Event processing and message routing
- Error handling and recovery
- Signal handling (SIGTERM, SIGINT)
- Resource cleanup

**Key Features**:
- Multi-threaded architecture for concurrent operations
- Queue-based processing for USB events
- Graceful shutdown with cleanup
- Automatic restart on failures
- System resource monitoring

**Threading Model**:
```
Main Thread:
├── Signal Handlers
├── Service Control
└── Event Loop

Worker Thread:
├── USB Processing Queue
├── File Operations
└── Network Operations

Monitor Thread:
├── USB Device Detection
└── Status Updates
```

### 2. USB Monitor (`usb_monitor.py`)

**Purpose**: Real-time USB device detection and monitoring

**Responsibilities**:
- USB device insertion/removal detection
- Device information extraction
- Mount point identification
- Event notification to main service

**Implementation Details**:
- **Primary Method**: pyudev for efficient event-driven monitoring
- **Fallback Method**: Polling-based detection every 2 seconds
- **Device Filtering**: USB storage devices only
- **Mount Verification**: Ensures devices are properly mounted

**Detection Process**:
```
USB Insertion → udev Event → Device Validation → Mount Check → 
Callback Trigger → Processing Queue
```

**Supported Detection Methods**:
1. **pyudev** (Preferred): Real-time udev events
2. **Polling**: Regular lsblk command execution
3. **Hybrid**: Automatic fallback if pyudev unavailable

### 3. Nextcloud Uploader (`nextcloud_uploader.py`)

**Purpose**: Nextcloud integration via WebDAV and OCS APIs

**Responsibilities**:
- File upload using WebDAV protocol
- Public share link creation via OCS API
- Directory management and creation
- Authentication and session management
- Error handling and retry logic

**API Integration**:
- **WebDAV API**: File operations (upload, delete, list)
- **OCS API**: Share management (create, configure, delete)
- **Authentication**: HTTP Basic Auth with app passwords
- **Security**: HTTPS enforcement, credential validation

**Upload Process**:
```
File → WebDAV Upload → Verify Upload → Create Public Share → 
Configure Permissions → Return Share URL
```

**Key Features**:
- Chunked upload support for large files
- Automatic directory creation
- Quota checking and validation
- Connection pooling and reuse
- Comprehensive error handling

### 4. Malware Scanner (`malware_scanner.py`)

**Purpose**: File security scanning using ClamAV

**Responsibilities**:
- Individual file scanning
- Directory traversal and scanning
- Infected file identification and quarantine
- Threat reporting and logging
- Database update management

**Scanning Process**:
```
File/Directory → ClamAV Scan → Threat Analysis → 
Safe/Infected Classification → Action (Upload/Block)
```

**Security Features**:
- Real-time virus database updates
- File size limits for scanning
- Timeout protection for large files
- Quarantine system for infected files
- Detailed threat reporting

### 5. File Processor (`file_processor.py`)

**Purpose**: File handling, compression, and packaging

**Responsibilities**:
- ZIP archive creation
- File filtering and exclusion
- Compression optimization
- Integrity verification
- Temporary file management

**Processing Pipeline**:
```
Source Files → Filter → Validate → Compress → Verify → 
Clean Temporary Files
```

**Archive Features**:
- Configurable compression levels
- File pattern exclusions
- Size limit enforcement
- Integrity checking
- Cross-platform compatibility

### 6. Email Notifier (`email_notifier.py`)

**Purpose**: Email notification system

**Responsibilities**:
- SMTP client management
- HTML email composition
- Download link delivery
- Delivery confirmation
- Error notification handling

**Email Features**:
- Professional HTML templates
- Embedded security information
- Mobile-friendly design
- Multiple recipient support
- Delivery status tracking

### 7. Status Manager (`status_manager.py`)

**Purpose**: Service status and inter-process communication

**Responsibilities**:
- Real-time status tracking
- Status persistence to disk
- Error logging and history
- Performance metrics
- External status queries

**Status Information**:
- Service state (idle, processing, error)
- Last activity timestamp
- Processing statistics
- Error history
- Uptime tracking

## Data Flow Architecture

### Processing Pipeline

```
┌─────────────────┐
│  USB Inserted   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐
│ Device Detection│────▶│ Mount Validation│
└─────────────────┘     └─────────┬───────┘
                                  │
                                  ▼
┌─────────────────┐     ┌─────────────────┐
│  File Discovery │◄────│   File System   │
└─────────┬───────┘     │    Traversal    │
          │             └─────────────────┘
          ▼
┌─────────────────┐
│ Malware Scanning│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐
│ Threat Analysis │────▶│  Safe Files     │
└─────────────────┘     └─────────┬───────┘
                                  │
                                  ▼
┌─────────────────┐     ┌─────────────────┐
│ Archive Creation│◄────│ File Processing │
└─────────┬───────┘     └─────────────────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐
│ Nextcloud Upload│────▶│ Upload Progress │
└─────────┬───────┘     └─────────────────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐
│  Share Creation │────▶│   Public Link   │
└─────────┬───────┘     └─────────────────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐
│  Email Input    │────▶│ User Interface  │
└─────────┬───────┘     └─────────────────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐
│Email Notification│───▶│   Delivery      │
└─────────┬───────┘     └─────────────────┘
          │
          ▼
┌─────────────────┐
│ Cleanup Schedule│
└─────────────────┘
```

### Error Handling Flow

```
┌─────────────────┐
│     Error       │
│   Detected      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐
│   Log Error     │────▶│  Error Details  │
└─────────┬───────┘     └─────────────────┘
          │
          ▼
┌─────────────────┐
│  Classify Error │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Recoverable   │────▶│  Retry Logic    │────▶│  Continue       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Non-Recoverable │────▶│  User Notify    │────▶│     Abort       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Technology Stack

### Core Technologies

**Python 3.7+**
- Primary programming language
- Extensive library ecosystem
- Cross-platform compatibility
- Strong community support

**systemd**
- Service management and auto-start
- Process supervision and restart
- Logging integration with journald
- Security and resource controls

**ClamAV**
- Open-source antivirus engine
- Regular virus database updates
- Command-line and library interfaces
- Real-time scanning capabilities

### Key Libraries and Dependencies

**Core Dependencies**:
- `requests`: HTTP client for Nextcloud API
- `configparser`: Configuration file management
- `pathlib`: Modern path handling
- `threading`: Multi-threaded processing
- `queue`: Thread-safe message passing

**Optional Dependencies**:
- `pyudev`: Efficient USB device monitoring
- `python-magic`: File type detection
- `clamd`: Python ClamAV interface

**System Dependencies**:
- `udev`: Device event system
- `mount`: File system mounting
- `lsblk`: Block device information
- `udevadm`: Device administration

### Network Protocols

**WebDAV (RFC 4918)**
- File upload and management
- PROPFIND for directory listing
- MKCOL for directory creation
- DELETE for file removal

**SMTP (RFC 5321)**
- Email delivery protocol
- STARTTLS for encryption
- Authentication support
- Multi-recipient capability

**HTTP/HTTPS**
- RESTful API communication
- TLS encryption for security
- Session management
- Error handling

## Design Patterns

### Observer Pattern

USB monitoring uses observer pattern for event handling:

```python
class USBMonitor:
    def __init__(self, on_insert_callback, on_remove_callback):
        self.on_insert_callback = on_insert_callback
        self.on_remove_callback = on_remove_callback
    
    def _device_inserted(self, device_info):
        self.on_insert_callback(device_info)
```

### Factory Pattern

Configuration management uses factory pattern:

```python
class ConfigManager:
    def get_cloud_config(self):
        return CloudConfigFactory.create(self.config)
    
    def get_email_config(self):
        return EmailConfigFactory.create(self.config)
```

### Strategy Pattern

File processing uses strategy pattern for different operations:

```python
class FileProcessor:
    def __init__(self):
        self.compression_strategy = ZipCompressionStrategy()
        self.filter_strategy = PatternFilterStrategy()
```

### Command Pattern

Processing queue uses command pattern for operations:

```python
class ProcessingCommand:
    def execute(self):
        raise NotImplementedError

class ScanCommand(ProcessingCommand):
    def execute(self):
        return self.scanner.scan_directory(self.path)
```

## Security Architecture

### Defense in Depth

**Layer 1: Input Validation**
- USB device validation
- File type checking
- Size limit enforcement
- Path sanitization

**Layer 2: Malware Scanning**
- ClamAV integration
- Real-time scanning
- Quarantine system
- Threat intelligence

**Layer 3: Network Security**
- HTTPS enforcement
- Certificate validation
- Secure authentication
- Encrypted communication

**Layer 4: System Security**
- Service isolation
- File permissions
- Resource limits
- Audit logging

### Threat Model

**Identified Threats**:
1. Malicious files on USB drives
2. Network interception
3. Credential compromise
4. System resource exhaustion
5. Configuration tampering

**Mitigations**:
1. Comprehensive malware scanning
2. End-to-end encryption
3. Secure credential storage
4. Resource monitoring and limits
5. Configuration file protection

## Performance Architecture

### Scalability Considerations

**File Processing**:
- Asynchronous I/O for large files
- Streaming processing for memory efficiency
- Concurrent scanning of multiple files
- Progress tracking and interruption

**Network Operations**:
- Connection pooling and reuse
- Chunked upload for large files
- Retry logic with exponential backoff
- Bandwidth throttling options

**Resource Management**:
- Memory usage monitoring
- Disk space management
- CPU usage optimization
- Network bandwidth control

### Optimization Strategies

**I/O Optimization**:
- Buffered file operations
- Efficient compression algorithms
- Parallel processing where possible
- Memory-mapped file access

**Network Optimization**:
- HTTP keep-alive connections
- Compression for API requests
- Efficient error handling
- Connection timeout management

## Deployment Architecture

### System Integration

**Service Management**:
```
systemd → pi-usb-safegate.service → daemon.py → Components
```

**File System Layout**:
```
/usr/share/pi-usb-safegate/    # Application files
/etc/pi-usb-safegate/          # Configuration
/var/log/pi-usb-safegate/      # Log files
/var/run/pi-usb-safegate/      # Runtime files
/usr/bin/                      # Executable scripts
```

**Process Management**:
- Single main process with multiple threads
- Automatic restart on failures
- Graceful shutdown handling
- Resource cleanup on exit

### Monitoring and Observability

**Logging Levels**:
- DEBUG: Detailed execution information
- INFO: Normal operations and status
- WARNING: Non-critical issues
- ERROR: Error conditions
- CRITICAL: System-threatening issues

**Metrics Collection**:
- Processing times and throughput
- Error rates and types
- Resource usage statistics
- Network performance metrics

**Health Checks**:
- Service availability
- Component functionality
- External service connectivity
- System resource status

## Future Architecture Considerations

### Extensibility

**Plugin Architecture**:
- Cloud provider plugins
- Scanner engine plugins
- Notification channel plugins
- File processor plugins

**API Extensions**:
- REST API for remote management
- WebSocket for real-time updates
- GraphQL for flexible queries
- Webhook support for integrations

### Scalability Improvements

**Horizontal Scaling**:
- Multi-device support
- Distributed processing
- Load balancing
- Cluster management

**Performance Enhancements**:
- GPU acceleration for scanning
- Machine learning threat detection
- Intelligent file prioritization
- Predictive caching

This architecture provides a robust, secure, and maintainable foundation for the Secure Nextcloud USB Uploader while allowing for future enhancements and extensions.