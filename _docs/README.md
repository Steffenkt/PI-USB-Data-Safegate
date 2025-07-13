# Secure Nextcloud USB Uploader

A headless Raspberry Pi application that continuously monitors for USB drives, scans files for malware, and uploads safe data to Nextcloud with automatic public sharing and email notifications.

## Overview

The Secure Nextcloud USB Uploader is a daemon-based application designed to run continuously on Raspberry Pi devices. It provides secure, automated file transfer from USB drives to Nextcloud cloud storage with the following key features:

- **Continuous USB Monitoring**: Detects USB drive insertion/removal in real-time
- **Malware Scanning**: Scans all files using ClamAV before upload
- **Nextcloud Integration**: Uploads files using WebDAV API with public link generation
- **Email Notifications**: Sends download links via email
- **Automatic Cleanup**: Removes files after configurable time period
- **Headless Operation**: Runs as a systemd service without user interaction
- **Minimal GUI**: Simple dialogs for email input and malware warnings

## Key Features

### 🔒 Security First
- **ClamAV Integration**: All files scanned for malware before upload
- **Infected File Handling**: Malware detected files are never uploaded
- **Secure Authentication**: Uses Nextcloud app passwords/tokens
- **HTTPS Communication**: All cloud transfers use encrypted connections

### 🚀 Automated Operation
- **Background Service**: Runs continuously as systemd daemon
- **Auto-Start**: Starts automatically on boot
- **Crash Recovery**: Automatic restart on failures
- **Event-Driven**: Responds immediately to USB insertion

### ☁️ Nextcloud Integration
- **WebDAV API**: Native Nextcloud file upload support
- **Public Sharing**: Automatic generation of public download links
- **Directory Management**: Automatic upload folder creation
- **Quota Awareness**: Monitors storage usage

### 📧 Email Notifications
- **SMTP Support**: Configurable email server settings
- **HTML Templates**: Professional email formatting
- **Download Links**: Direct links to uploaded files
- **Error Notifications**: Alerts for malware detection

### 🗂️ File Management
- **ZIP Compression**: Efficient file packaging
- **Automatic Cleanup**: Configurable file deletion
- **Processing Queue**: Handles multiple USB drives
- **Progress Tracking**: Real-time status updates

## System Requirements

### Hardware
- Raspberry Pi (any model with USB ports)
- Minimum 512MB RAM
- 1GB free storage space
- USB ports for drive connection
- Network connectivity (WiFi or Ethernet)

### Software
- Raspberry Pi OS (Bullseye or newer)
- Python 3.7+
- ClamAV antivirus software
- Nextcloud server access
- Email server access (SMTP)

### Network
- Internet connection for cloud uploads
- Access to Nextcloud server
- SMTP server access for email notifications

## Quick Start

### 1. Installation
```bash
# Clone repository
git clone https://github.com/example/secure-nextcloud-usb-uploader.git
cd secure-nextcloud-usb-uploader

# Run installation script
sudo ./install.sh

# Or build and install package
./build-package.sh
sudo dpkg -i pi-usb-safegate_1.0.0_all.deb
```

### 2. Configuration
```bash
# Edit configuration file
sudo nano /etc/pi-usb-safegate/config.ini

# Configure Nextcloud and email settings
# See CONFIG.md for detailed options
```

### 3. Start Service
```bash
# Start the daemon
sudo systemctl start pi-usb-safegate

# Enable auto-start on boot
sudo systemctl enable pi-usb-safegate

# Check status
sudo systemctl status pi-usb-safegate
```

### 4. Usage
1. Insert USB drive into Raspberry Pi
2. Service automatically detects and scans files
3. Enter email address when prompted
4. Receive download link via email
5. Files automatically deleted after 7 days

## Architecture

### Core Components

1. **Daemon Service** (`daemon.py`)
   - Main service process
   - Coordinates all components
   - Handles USB device events

2. **USB Monitor** (`usb_monitor.py`)
   - Detects USB insertion/removal
   - Uses udev for efficient monitoring
   - Supports pyudev and polling methods

3. **Nextcloud Uploader** (`nextcloud_uploader.py`)
   - WebDAV API integration
   - File upload functionality
   - Public share link generation

4. **Malware Scanner** (`malware_scanner.py`)
   - ClamAV integration
   - Virus scanning and detection
   - Infected file reporting

5. **Email Notifier** (`email_notifier.py`)
   - SMTP email sending
   - HTML email templates
   - Download link delivery

6. **Status Manager** (`status_manager.py`)
   - Service status tracking
   - Inter-process communication
   - Error reporting

### Process Flow

```
USB Inserted → Malware Scan → Clean Files → ZIP Archive → 
Nextcloud Upload → Public Share → Email Notification → 
Schedule Cleanup → Complete
```

## Configuration

Configuration is managed through `/etc/pi-usb-safegate/config.ini`:

```ini
[NEXTCLOUD]
url = https://your-nextcloud.com
username = your_username
password = your_app_password
upload_path = /USB_Transfers

[EMAIL]
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_username = your_email@gmail.com
smtp_password = your_app_password

[SECURITY]
clamav_db_path = /var/lib/clamav
max_file_size_mb = 100

[CLEANUP]
auto_delete_days = 7
cleanup_check_interval_hours = 24
```

See [CONFIG.md](CONFIG.md) for complete configuration options.

## Service Management

### Using systemctl
```bash
# Start service
sudo systemctl start pi-usb-safegate

# Stop service
sudo systemctl stop pi-usb-safegate

# Restart service
sudo systemctl restart pi-usb-safegate

# Check status
sudo systemctl status pi-usb-safegate

# View logs
sudo journalctl -u pi-usb-safegate -f
```

### Using daemon-control.sh
```bash
# Service control
sudo ./daemon-control.sh start
sudo ./daemon-control.sh stop
sudo ./daemon-control.sh restart
sudo ./daemon-control.sh status

# Auto-start management
sudo ./daemon-control.sh enable
sudo ./daemon-control.sh disable

# Logs
sudo ./daemon-control.sh logs
sudo ./daemon-control.sh logs-follow
```

## Monitoring

### Status Checking
```bash
# Check service status
sudo systemctl status pi-usb-safegate

# View real-time logs
sudo journalctl -u pi-usb-safegate -f

# Check daemon status
python3 -c "from modules.status_manager import StatusManager; print(StatusManager.read_status())"
```

### Log Files
- **Service Logs**: `journalctl -u pi-usb-safegate`
- **Daemon Logs**: `/var/log/pi-usb-safegate/daemon.log`
- **Application Logs**: `/var/log/pi-usb-safegate/safegate.log`

## Security Considerations

### Data Protection
- All files scanned for malware before upload
- Infected files are never uploaded to cloud storage
- Automatic file cleanup prevents long-term storage
- Secure authentication using app passwords

### Network Security
- HTTPS used for all cloud communications
- SMTP with TLS for email notifications
- No sensitive data stored in logs
- Configurable security settings

### System Security
- Service runs with minimal privileges
- Temporary files cleaned after processing
- Protected configuration files
- Audit logging for all operations

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check ClamAV installation: `sudo systemctl status clamav-daemon`
   - Verify configuration: `sudo nano /etc/pi-usb-safegate/config.ini`
   - Check logs: `sudo journalctl -u pi-usb-safegate`

2. **USB drives not detected**
   - Check USB mount permissions
   - Verify udev rules installation
   - Test with different USB ports

3. **Upload failures**
   - Test Nextcloud credentials
   - Check network connectivity
   - Verify upload directory exists

4. **Email not sending**
   - Verify SMTP settings
   - Test email credentials
   - Check firewall settings

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

## Development

### Project Structure
```
PI-USB-Data-Safegate/
├── src/                      # Source code
│   └── pi_usb_safegate/     # Main package
│       ├── daemon.py        # Main daemon service
│       ├── main.py          # GUI application
│       ├── version.py       # Version management
│       └── modules/         # Core modules
│           ├── usb_monitor.py       # USB device monitoring
│           ├── nextcloud_uploader.py # Nextcloud integration
│           ├── malware_scanner.py   # ClamAV integration
│           └── ...
├── scripts/                 # Build and utility scripts
│   ├── build-package.sh     # Package builder
│   ├── bump-version.py      # Version management
│   └── install.sh           # Installation script
├── config/                  # Configuration files
├── tests/                   # Test files
├── packaging/               # Debian packaging
├── _docs/                   # Documentation
└── README.md
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request
5. Follow coding standards

### Dependencies
- `requests` - HTTP client for Nextcloud API
- `pyudev` - USB device monitoring (optional)
- `clamd` - ClamAV integration
- `python-magic` - File type detection

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: Complete guides in `_docs/` folder
- **Issues**: Report bugs and request features
- **Community**: Join discussions and get help
- **Development**: Contribute code and improvements

## Acknowledgments

- **ClamAV**: Open-source antivirus engine
- **Nextcloud**: Open-source cloud platform
- **Raspberry Pi**: Affordable computing platform
- **Python**: Programming language and ecosystem