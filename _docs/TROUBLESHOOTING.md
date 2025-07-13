# Troubleshooting Guide

This comprehensive guide helps diagnose and resolve common issues with the Secure Nextcloud USB Uploader.

## Quick Diagnostics

### Health Check Commands

```bash
# Check service status
sudo systemctl status pi-usb-safegate

# Test all components
sudo ./daemon-control.sh test

# View recent logs
sudo journalctl -u pi-usb-safegate -n 50

# Check configuration
sudo python3 -c "from modules.config_manager import ConfigManager; ConfigManager()"

# Verify dependencies
sudo systemctl status clamav-daemon
```

### Status Indicators

| Status | Meaning | Action Required |
|--------|---------|----------------|
| `active (running)` | Service operational | None |
| `failed` | Service crashed | Check logs, restart |
| `inactive (dead)` | Service stopped | Start service |
| `activating` | Service starting | Wait or check logs |

## Common Issues and Solutions

### 1. Service Won't Start

#### Symptoms
- `sudo systemctl start pi-usb-safegate` fails
- Service shows "failed" status
- Error in logs: "Failed to start"

#### Diagnosis
```bash
# Check detailed service status
sudo systemctl status pi-usb-safegate -l

# Check service logs
sudo journalctl -u pi-usb-safegate -f

# Test daemon directly
sudo python3 /usr/share/pi-usb-safegate/daemon.py test
```

#### Common Causes and Solutions

**1. ClamAV Not Running**
```bash
# Check ClamAV status
sudo systemctl status clamav-daemon

# Start ClamAV if stopped
sudo systemctl start clamav-daemon
sudo systemctl enable clamav-daemon

# Update virus database
sudo freshclam
```

**2. Configuration Errors**
```bash
# Validate configuration
sudo python3 -c "
from modules.config_manager import ConfigManager
try:
    config = ConfigManager()
    print('Configuration valid')
except Exception as e:
    print(f'Configuration error: {e}')
"

# Check config file syntax
sudo nano /etc/pi-usb-safegate/config.ini
```

**3. Permission Issues**
```bash
# Fix file permissions
sudo chown -R root:root /usr/share/pi-usb-safegate/
sudo chmod 755 /usr/share/pi-usb-safegate/
sudo chmod 644 /usr/share/pi-usb-safegate/*.py
sudo chmod 755 /usr/share/pi-usb-safegate/daemon.py

# Fix log directory permissions
sudo mkdir -p /var/log/pi-usb-safegate
sudo chown root:root /var/log/pi-usb-safegate
sudo chmod 755 /var/log/pi-usb-safegate
```

**4. Missing Dependencies**
```bash
# Install Python dependencies
pip3 install requests configparser pathlib

# Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-tk clamav udev
```

### 2. USB Drives Not Detected

#### Symptoms
- USB insertion doesn't trigger processing
- No activity in logs when USB inserted
- Service running but not responding to devices

#### Diagnosis
```bash
# Check USB devices
lsusb
lsblk

# Check mount points
df -h | grep media
mount | grep usb

# Test USB detection manually
sudo python3 -c "
from modules.usb_monitor import USBMonitor
monitor = USBMonitor(lambda x: print(f'Inserted: {x}'), lambda x: print(f'Removed: {x}'))
devices = monitor._get_usb_storage_devices()
print(f'USB devices found: {devices}')
"
```

#### Solutions

**1. USB Not Mounted**
```bash
# Check if device is detected but not mounted
lsblk

# Manual mount if needed
sudo mkdir -p /mnt/usb
sudo mount /dev/sda1 /mnt/usb

# Check auto-mount configuration
cat /etc/fstab
```

**2. udev Rules Missing**
```bash
# Check udev rules
ls -la /etc/udev/rules.d/ | grep usb

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Test udev monitoring
sudo udevadm monitor --subsystem-match=block
```

**3. File System Not Supported**
```bash
# Check file system type
sudo blkid /dev/sda1

# Install additional file system support
sudo apt install ntfs-3g exfat-fuse exfat-utils
```

**4. pyudev Issues**
```bash
# Install pyudev
pip3 install pyudev

# Test pyudev functionality
python3 -c "
import pyudev
context = pyudev.Context()
print('pyudev working')
"

# If pyudev fails, service will use polling method
```

### 3. Malware Scanning Failures

#### Symptoms
- Error: "ClamAV not available"
- Files not being scanned
- Service hangs during scanning

#### Diagnosis
```bash
# Check ClamAV installation
clamscan --version

# Check ClamAV service
sudo systemctl status clamav-daemon
sudo systemctl status clamav-freshclam

# Test manual scan
clamscan /tmp/eicar.com

# Check ClamAV logs
sudo tail -f /var/log/clamav/clamav.log
```

#### Solutions

**1. ClamAV Not Installed**
```bash
# Install ClamAV
sudo apt update
sudo apt install clamav clamav-daemon clamav-freshclam

# Start services
sudo systemctl enable clamav-daemon
sudo systemctl enable clamav-freshclam
sudo systemctl start clamav-daemon
sudo systemctl start clamav-freshclam
```

**2. Virus Database Outdated**
```bash
# Update virus database
sudo freshclam

# Check database status
sudo systemctl status clamav-freshclam

# Manual database update
sudo systemctl stop clamav-freshclam
sudo freshclam
sudo systemctl start clamav-freshclam
```

**3. ClamAV Configuration Issues**
```bash
# Check ClamAV configuration
sudo nano /etc/clamav/clamd.conf

# Ensure these settings:
# LocalSocket /var/run/clamav/clamd.ctl
# User clamav

# Restart ClamAV
sudo systemctl restart clamav-daemon
```

**4. Large File Timeouts**
```bash
# Increase scan timeout in config
sudo nano /etc/pi-usb-safegate/config.ini

# Add/modify:
[SECURITY]
scan_timeout = 600
max_file_size_mb = 200
```

### 4. Nextcloud Upload Failures

#### Symptoms
- Error: "Upload failed"
- "Authentication failed"
- "Connection timeout"

#### Diagnosis
```bash
# Test Nextcloud connection
sudo python3 -c "
from modules.nextcloud_uploader import NextcloudUploader
from modules.config_manager import ConfigManager
uploader = NextcloudUploader(ConfigManager())
print(f'Connection test: {uploader.test_connection()}')
"

# Test manual WebDAV access
curl -u username:password -X PROPFIND https://your-nextcloud.com/remote.php/dav/files/username/

# Check network connectivity
ping your-nextcloud.com
nslookup your-nextcloud.com
```

#### Solutions

**1. Invalid Credentials**
```bash
# Check configuration
sudo nano /etc/pi-usb-safegate/config.ini

# Verify credentials in browser:
# https://your-nextcloud.com
# Settings → Security → Devices & sessions → Create new app password

# Test credentials manually
curl -u username:app_password https://your-nextcloud.com/status.php
```

**2. Network Connectivity Issues**
```bash
# Check network status
ip route show
ping 8.8.8.8

# Check DNS resolution
nslookup your-nextcloud.com

# Check firewall
sudo ufw status
```

**3. SSL Certificate Issues**
```bash
# Test SSL certificate
openssl s_client -connect your-nextcloud.com:443

# Update CA certificates
sudo apt update
sudo apt install ca-certificates
sudo update-ca-certificates
```

**4. Upload Directory Issues**
```bash
# Check if upload directory exists
# Login to Nextcloud web interface
# Navigate to specified upload path
# Create directory if missing

# Or create via WebDAV
curl -u username:password -X MKCOL https://your-nextcloud.com/remote.php/dav/files/username/USB_Transfers/
```

### 5. Email Notification Failures

#### Symptoms
- "Failed to send email"
- No email received
- SMTP authentication errors

#### Diagnosis
```bash
# Test email configuration
sudo python3 -c "
from modules.email_notifier import EmailNotifier
from modules.config_manager import ConfigManager
notifier = EmailNotifier(ConfigManager())
print(f'Email test: {notifier.test_email_connection()}')
"

# Test SMTP manually
telnet smtp.gmail.com 587
```

#### Solutions

**1. SMTP Configuration Issues**
```bash
# Check email configuration
sudo nano /etc/pi-usb-safegate/config.ini

# For Gmail:
[EMAIL]
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_username = your_email@gmail.com
smtp_password = your_app_password
use_tls = true

# Generate Gmail app password:
# Google Account → Security → 2-Step Verification → App passwords
```

**2. Authentication Failures**
```bash
# For Gmail - ensure 2FA enabled and app password used
# For Outlook - use account password or app password
# For custom servers - verify SMTP settings

# Test with different email client first
```

**3. Network/Firewall Issues**
```bash
# Check if SMTP ports are blocked
sudo netstat -tulpn | grep :587
sudo netstat -tulpn | grep :465

# Test SMTP connectivity
telnet smtp.gmail.com 587
nc -zv smtp.gmail.com 587
```

### 6. File Processing Issues

#### Symptoms
- ZIP creation fails
- "No files found"
- Processing hangs

#### Diagnosis
```bash
# Check available disk space
df -h

# Check file permissions on USB
ls -la /media/*/

# Test file processing manually
sudo python3 -c "
from modules.file_processor import FileProcessor
processor = FileProcessor()
files = ['/tmp/test.txt']
with open('/tmp/test.txt', 'w') as f: f.write('test')
zip_path = processor.create_zip(files)
print(f'ZIP created: {zip_path}')
"
```

#### Solutions

**1. Insufficient Disk Space**
```bash
# Check disk usage
df -h

# Clean up temporary files
sudo rm -rf /tmp/safegate_*
sudo rm -rf /var/tmp/pi-usb-*

# Clean up old logs
sudo journalctl --vacuum-time=7d
```

**2. File Permission Issues**
```bash
# Check USB drive permissions
ls -la /media/*/

# Mount with proper permissions if needed
sudo umount /dev/sda1
sudo mount -o uid=1000,gid=1000 /dev/sda1 /media/usb/
```

**3. File System Corruption**
```bash
# Check file system
sudo fsck /dev/sda1

# Try different USB port
# Try different USB device
```

### 7. Service Performance Issues

#### Symptoms
- Slow processing
- High CPU/memory usage
- Timeouts

#### Diagnosis
```bash
# Check system resources
top
htop
free -h
iostat

# Check service resource usage
sudo systemctl status pi-usb-safegate
ps aux | grep python3

# Monitor file operations
sudo iotop
```

#### Solutions

**1. Resource Optimization**
```bash
# Adjust configuration for better performance
sudo nano /etc/pi-usb-safegate/config.ini

[PROCESSING]
zip_compression_level = 1
max_archive_size_mb = 500

[SECURITY]
max_file_size_mb = 50
scan_timeout = 300
```

**2. System Optimization**
```bash
# Increase swap if needed
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Clean up system
sudo apt autoremove
sudo apt autoclean
```

## Advanced Troubleshooting

### Debug Mode

#### Enable Debug Logging
```bash
# Edit configuration
sudo nano /etc/pi-usb-safegate/config.ini

[LOGGING]
log_level = DEBUG

# Restart service
sudo systemctl restart pi-usb-safegate

# Watch debug logs
sudo journalctl -u pi-usb-safegate -f
```

#### Manual Debug Run
```bash
# Stop service
sudo systemctl stop pi-usb-safegate

# Run daemon manually with debug
sudo python3 /usr/share/pi-usb-safegate/daemon.py start --debug

# In another terminal, monitor status
watch "sudo ./daemon-control.sh status"
```

### Component Testing

#### Test Individual Components
```bash
# Test configuration loading
python3 -c "from modules.config_manager import ConfigManager; print(ConfigManager().get_cloud_config())"

# Test USB detection
python3 -c "from modules.usb_detector import USBDetector; print(USBDetector().get_usb_drives())"

# Test ClamAV scanner
python3 -c "from modules.malware_scanner import MalwareScanner; print(MalwareScanner()._check_clamav_availability())"

# Test Nextcloud connection
python3 -c "from modules.nextcloud_uploader import NextcloudUploader; from modules.config_manager import ConfigManager; print(NextcloudUploader(ConfigManager()).test_connection())"
```

### Log Analysis

#### Important Log Patterns
```bash
# Service startup
sudo journalctl -u pi-usb-safegate | grep "Starting"

# USB detection
sudo journalctl -u pi-usb-safegate | grep "USB device"

# Error patterns
sudo journalctl -u pi-usb-safegate | grep -E "(ERROR|CRITICAL|Failed)"

# Processing statistics
sudo journalctl -u pi-usb-safegate | grep "Processing complete"
```

#### Log Locations
- **Service Logs**: `journalctl -u pi-usb-safegate`
- **Daemon Logs**: `/var/log/pi-usb-safegate/daemon.log`
- **ClamAV Logs**: `/var/log/clamav/clamav.log`
- **System Logs**: `/var/log/syslog`

### Network Diagnostics

#### Connectivity Testing
```bash
# Test basic connectivity
ping 8.8.8.8

# Test DNS resolution
nslookup your-nextcloud.com

# Test HTTPS connectivity
curl -I https://your-nextcloud.com

# Test SMTP connectivity
nc -zv smtp.gmail.com 587
```

#### Packet Capture
```bash
# Capture network traffic (if needed)
sudo tcpdump -i any host your-nextcloud.com

# Monitor specific ports
sudo netstat -tulpn | grep -E "(587|465|80|443)"
```

## Recovery Procedures

### Complete Service Reset

```bash
# Stop service
sudo systemctl stop pi-usb-safegate

# Clear runtime state
sudo rm -rf /var/run/pi-usb-safegate/

# Clear temporary files
sudo rm -rf /tmp/safegate_*

# Reset logs (optional)
sudo rm -f /var/log/pi-usb-safegate/*

# Start service
sudo systemctl start pi-usb-safegate
```

### Configuration Reset

```bash
# Backup current config
sudo cp /etc/pi-usb-safegate/config.ini /etc/pi-usb-safegate/config.ini.backup

# Reset to defaults
sudo cp /etc/pi-usb-safegate/config.ini.template /etc/pi-usb-safegate/config.ini

# Edit with your settings
sudo nano /etc/pi-usb-safegate/config.ini

# Restart service
sudo systemctl restart pi-usb-safegate
```

### System Recovery

```bash
# Update system
sudo apt update && sudo apt upgrade

# Reinstall ClamAV
sudo apt remove --purge clamav clamav-daemon
sudo apt install clamav clamav-daemon clamav-freshclam

# Update virus database
sudo freshclam

# Reinstall application
sudo dpkg -i pi-usb-safegate_*.deb
```

## Getting Help

### Information to Collect

When seeking help, collect this information:

```bash
# System information
uname -a
cat /etc/os-release

# Service status
sudo systemctl status pi-usb-safegate --no-pager -l

# Recent logs
sudo journalctl -u pi-usb-safegate -n 100 --no-pager

# Configuration (remove sensitive data)
sudo cat /etc/pi-usb-safegate/config.ini

# Component tests
sudo ./daemon-control.sh test
```

### Support Channels

1. **Documentation**: Check all files in `_docs/` folder
2. **Logs**: Always check logs first for error details
3. **Configuration**: Verify all settings in config.ini
4. **Dependencies**: Ensure all required software is installed
5. **Community**: GitHub issues and discussions

### Creating Bug Reports

Include this information in bug reports:

1. **System Details**: OS version, hardware model
2. **Steps to Reproduce**: Exact steps that cause the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Logs**: Relevant log entries
6. **Configuration**: Sanitized config file
7. **Workarounds**: Any temporary solutions found

## Prevention

### Regular Maintenance

```bash
# Weekly maintenance script
#!/bin/bash

# Update ClamAV database
sudo freshclam

# Check service status
sudo systemctl status pi-usb-safegate

# Clean old logs
sudo journalctl --vacuum-time=30d

# Check disk space
df -h

# Update system
sudo apt update && sudo apt list --upgradable
```

### Monitoring

```bash
# Add to crontab for monitoring
# Check service every 5 minutes
*/5 * * * * systemctl is-active --quiet pi-usb-safegate || echo "Service down" | mail admin@example.com
```

### Backup

```bash
# Backup configuration
sudo cp /etc/pi-usb-safegate/config.ini ~/config-backup-$(date +%Y%m%d).ini

# Backup important logs
sudo cp /var/log/pi-usb-safegate/daemon.log ~/daemon-log-backup-$(date +%Y%m%d).log
```

This troubleshooting guide covers the most common issues and their solutions. For complex problems, systematic diagnosis using the provided commands and procedures will help identify the root cause and appropriate solution.