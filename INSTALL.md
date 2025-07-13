# PI USB Data Safegate Installation Guide

A comprehensive guide for installing PI USB Data Safegate on Raspberry Pi OS and other Debian-based systems.

## Quick Start

### Option 1: Using the Debian Package (Recommended)

1. **Build the package** (or download pre-built):
   ```bash
   chmod +x build-package.sh
   ./build-package.sh
   ```

2. **Install the package**:
   ```bash
   sudo dpkg -i pi-usb-safegate_1.0.0_all.deb
   ```

3. **Fix any dependency issues**:
   ```bash
   sudo apt --fix-broken install
   ```

4. **Configure the application**:
   ```bash
   sudo pi-usb-safegate-setup
   ```

5. **Run the application**:
   ```bash
   sudo pi-usb-safegate
   ```

### Option 2: Using the Automated Install Script

1. **Make the script executable**:
   ```bash
   chmod +x install.sh
   ```

2. **Run the installer**:
   ```bash
   sudo ./install.sh
   ```

3. **Configure the application**:
   ```bash
   sudo pi-usb-safegate-setup
   ```

## System Requirements

### Hardware Requirements
- Raspberry Pi (any model) or compatible ARM/x86 Linux system
- Minimum 1GB RAM
- 2GB free disk space
- USB ports for connecting drives
- Internet connection for cloud uploads and email

### Software Requirements
- Raspberry Pi OS (Bullseye or newer) or Ubuntu/Debian
- Python 3.7 or higher
- Root access (sudo privileges)

## Pre-Installation Setup

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Build Tools (if building from source)
```bash
sudo apt install -y build-essential git
```

### 3. Clone Repository (if needed)
```bash
git clone https://github.com/example/pi-usb-safegate.git
cd pi-usb-safegate
```

## Installation Methods

### Method 1: Debian Package Installation

#### Building the Package
```bash
# Install build dependencies
sudo apt install -y dpkg-dev lintian fakeroot

# Build the package
make build

# Or use the build script directly
./build-package.sh
```

#### Installing the Package
```bash
# Install the built package
sudo dpkg -i pi-usb-safegate_1.0.0_all.deb

# Fix any dependency issues
sudo apt --fix-broken install

# Verify installation
dpkg -l | grep pi-usb-safegate
```

### Method 2: Source Installation

#### Using the Install Script
```bash
# Run the automated installer
sudo ./install.sh
```

#### Manual Installation
```bash
# Install system dependencies
sudo apt install -y python3 python3-pip python3-tk python3-dev \
    clamav clamav-daemon clamav-freshclam udev mount util-linux curl wget

# Install Python dependencies
pip3 install -r requirements.txt

# Update ClamAV database
sudo freshclam

# Copy files to system locations
sudo cp -r . /usr/share/pi-usb-safegate/
sudo cp config.ini /etc/pi-usb-safegate/
# ... (continue with manual setup)
```

## Post-Installation Configuration

### 1. Initial Configuration
```bash
# Run the configuration wizard
sudo pi-usb-safegate-setup
```

### 2. Manual Configuration
Edit the configuration file:
```bash
sudo nano /etc/pi-usb-safegate/config.ini
```

#### Email Configuration
```ini
[EMAIL]
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_username = your_email@gmail.com
smtp_password = your_app_password
sender_name = PI USB Data Safegate
```

#### Cloud Storage Configuration

**For Nextcloud:**
```ini
[CLOUD_STORAGE]
provider = nextcloud
nextcloud_url = https://your-nextcloud.com
nextcloud_username = your_username
nextcloud_password = your_password
nextcloud_upload_path = /USB_Transfers
```

**For Dropbox:**
```ini
[CLOUD_STORAGE]
provider = dropbox
dropbox_access_token = your_dropbox_token
```

### 3. Enable Background Services (Optional)
```bash
# Enable automatic cleanup service
sudo systemctl enable pi-usb-safegate-cleanup.timer
sudo systemctl start pi-usb-safegate-cleanup.timer

# Check service status
sudo systemctl status pi-usb-safegate-cleanup.timer
```

## Usage

### Starting the Application

#### From Command Line
```bash
sudo pi-usb-safegate
```

#### From Desktop
Find "PI USB Data Safegate" in your applications menu under System → Security

### Basic Workflow
1. **Connect USB Drive**: Insert USB drive into Raspberry Pi
2. **Launch Application**: Start PI USB Data Safegate
3. **Select Drive**: Choose USB drive from dropdown
4. **Enter Email**: Provide email address for notifications
5. **Process Files**: Click "Scan and Upload Files"
6. **Monitor Progress**: Watch real-time status updates
7. **Receive Email**: Download link sent to your email

## File Locations

### System Installation
- **Application files**: `/usr/share/pi-usb-safegate/`
- **Configuration**: `/etc/pi-usb-safegate/config.ini`
- **Log files**: `/var/log/pi-usb-safegate/`
- **Executable**: `/usr/bin/pi-usb-safegate`
- **Desktop entry**: `/usr/share/applications/pi-usb-safegate.desktop`

### Source Installation
- **Application files**: Current directory
- **Configuration**: `config.ini`
- **Log files**: `safegate.log`

## Troubleshooting

### Common Issues

#### 1. Permission Errors
```bash
# Ensure running as root
sudo pi-usb-safegate

# Check file permissions
ls -la /usr/share/pi-usb-safegate/
```

#### 2. ClamAV Issues
```bash
# Update virus database
sudo freshclam

# Restart ClamAV services
sudo systemctl restart clamav-daemon
sudo systemctl restart clamav-freshclam

# Check ClamAV status
sudo systemctl status clamav-daemon
```

#### 3. USB Drive Not Detected
```bash
# Check connected drives
lsblk

# Check USB devices
lsusb

# Manual mount if needed
sudo mkdir -p /mnt/usb
sudo mount /dev/sda1 /mnt/usb
```

#### 4. Email Not Sending
- Verify SMTP settings in config.ini
- For Gmail: Use App Password instead of regular password
- Check firewall settings for SMTP ports (587, 465)
- Test with simple email client

#### 5. Cloud Upload Failures
- Check internet connection
- Verify cloud storage credentials
- Ensure upload directory exists
- Check cloud storage quotas

### Log Analysis
```bash
# View application logs
sudo tail -f /var/log/pi-usb-safegate/safegate.log

# View system logs
sudo journalctl -u pi-usb-safegate-cleanup.service

# Check ClamAV logs
sudo tail -f /var/log/clamav/clamav.log
```

### Getting Help
1. Check application logs for error messages
2. Verify configuration settings
3. Test individual components (email, cloud storage)
4. Review system requirements
5. Check GitHub issues for known problems

## Uninstallation

### Remove Package
```bash
# Remove application but keep configuration
sudo apt remove pi-usb-safegate

# Remove everything including configuration
sudo apt purge pi-usb-safegate
```

### Using Uninstall Script
```bash
# Interactive uninstall
sudo ./uninstall.sh
```

### Manual Removal
```bash
# Stop services
sudo systemctl stop pi-usb-safegate-cleanup.timer
sudo systemctl disable pi-usb-safegate-cleanup.timer

# Remove files
sudo rm -rf /usr/share/pi-usb-safegate/
sudo rm -rf /etc/pi-usb-safegate/
sudo rm -rf /var/log/pi-usb-safegate/
sudo rm -f /usr/bin/pi-usb-safegate*
sudo rm -f /usr/share/applications/pi-usb-safegate.desktop
```

## Advanced Configuration

### Custom Email Templates
Edit the email template in:
```bash
sudo nano /usr/share/pi-usb-safegate/modules/email_notifier.py
```

### Modify Cleanup Schedule
```bash
# Edit cleanup configuration
sudo nano /etc/pi-usb-safegate/config.ini

# Manually trigger cleanup
sudo python3 -c "
from modules.cleanup_scheduler import CleanupScheduler
from modules.config_manager import ConfigManager
cs = CleanupScheduler(ConfigManager())
cs.check_and_cleanup()
"
```

### Add Custom File Filters
Edit file processing rules:
```bash
sudo nano /usr/share/pi-usb-safegate/modules/file_processor.py
```

## Security Considerations

### Best Practices
1. **Regular Updates**: Keep system and application updated
2. **Virus Database**: Update ClamAV database regularly
3. **Secure Credentials**: Use app passwords for email
4. **Network Security**: Use HTTPS for all cloud communications
5. **Access Control**: Limit physical access to Raspberry Pi
6. **Backup**: Regular backup of configuration files

### Security Features
- ✅ Malware scanning before upload
- ✅ Encrypted cloud transfers (HTTPS)
- ✅ Automatic file cleanup
- ✅ Secure email notifications
- ✅ Root privilege requirement
- ✅ Configuration file protection

## Support and Development

### Getting Support
- Check troubleshooting section
- Review log files for errors
- Verify system requirements
- Test configuration settings

### Contributing
- Report bugs via GitHub issues
- Submit pull requests for improvements
- Follow coding standards
- Maintain security focus

### Building from Source
```bash
# Clone repository
git clone https://github.com/example/pi-usb-safegate.git
cd pi-usb-safegate

# Install development dependencies
sudo apt install -y python3-dev build-essential

# Build package
make build

# Run tests
make test

# Install for development
make dev-install
```

## Frequently Asked Questions

### Q: Why does the application require root privileges?
A: Root privileges are required to access USB devices, mount filesystems, and write to system directories securely.

### Q: How is malware detection performed?
A: The application uses ClamAV to scan all files before upload. Only files that pass scanning are included in the upload.

### Q: What happens to infected files?
A: Infected files are logged and excluded from upload. They can optionally be quarantined based on configuration.

### Q: Can I use other cloud storage providers?
A: Currently supports Nextcloud and Dropbox. Additional providers can be added by extending the cloud_uploader module.

### Q: How long are files kept in cloud storage?
A: Files are automatically deleted after 7 days (configurable) to maintain security and storage efficiency.

### Q: Can I run this on other Linux distributions?
A: Yes, it should work on any Debian-based distribution. Other distributions may require package name adjustments.

---

**Note**: This application is designed for security-conscious users who need to safely transfer files from USB drives to cloud storage. Always ensure your system is updated and follow security best practices.