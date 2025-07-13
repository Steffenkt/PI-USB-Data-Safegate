# Usage Guide

This guide covers how to run, use, and monitor the Secure Nextcloud USB Uploader.

## Overview

The Secure Nextcloud USB Uploader operates as a headless daemon service that continuously monitors for USB drive insertions. When a USB drive is detected, the system automatically:

1. Scans all files for malware using ClamAV
2. Creates a ZIP archive of safe files
3. Uploads the archive to Nextcloud
4. Generates a public share link
5. Prompts for email address via GUI
6. Sends download link via email
7. Schedules automatic cleanup

## Starting the Service

### Method 1: Using systemctl (Recommended)

```bash
# Start the service
sudo systemctl start pi-usb-safegate

# Enable auto-start on boot
sudo systemctl enable pi-usb-safegate

# Check service status
sudo systemctl status pi-usb-safegate
```

### Method 2: Using Daemon Control Script

```bash
# Start service
sudo ./daemon-control.sh start

# Enable auto-start
sudo ./daemon-control.sh enable

# Check status
sudo ./daemon-control.sh status
```

### Method 3: Manual Execution (Development)

```bash
# Run daemon directly
sudo python3 daemon.py start

# Run with debug output
sudo python3 daemon.py start --debug
```

## Basic Workflow

### Step-by-Step Process

1. **Insert USB Drive**
   - Connect USB storage device to Raspberry Pi
   - Service automatically detects the new device
   - Processing begins immediately

2. **Malware Scanning**
   - All files scanned using ClamAV
   - Progress shown in logs
   - If malware detected: GUI warning displayed, files NOT uploaded
   - If clean: Processing continues

3. **File Processing**
   - Safe files compressed into ZIP archive
   - Archive created in temporary directory
   - Original files remain on USB drive

4. **Nextcloud Upload**
   - ZIP archive uploaded to configured Nextcloud directory
   - Upload progress logged
   - Remote file path recorded

5. **Public Share Creation**
   - Public download link generated via Nextcloud API
   - Link configured with expiration (if set)
   - Share permissions set to read-only

6. **Email Input**
   - GUI dialog prompts for email address
   - User enters recipient email
   - Email validation performed

7. **Email Notification**
   - Professional HTML email sent with download link
   - Email includes file information and security notes
   - Delivery confirmation logged

8. **Cleanup Scheduling**
   - File scheduled for automatic deletion
   - Default: 7 days after upload
   - Cleanup database updated

## User Interactions

### Email Address Input

When files are ready for sharing, a GUI dialog appears:

```
┌─────────────────────────────────────┐
│           Email Address             │
├─────────────────────────────────────┤
│ Enter email address to receive      │
│ download link:                      │
│                                     │
│ [____________________________]     │
│                                     │
│         [OK]    [Cancel]            │
└─────────────────────────────────────┘
```

**Tips:**
- Enter valid email address
- Check spam folder for delivery
- Link expires based on configuration
- Multiple emails can be sent by re-inserting USB

### Malware Warning Dialog

If malware is detected, a warning dialog appears:

```
┌─────────────────────────────────────┐
│        ⚠️  MALWARE DETECTED!  ⚠️        │
├─────────────────────────────────────┤
│ Found 2 infected files:             │
│                                     │
│ • document.pdf: Trojan.GenKB       │
│ • setup.exe: Malware.Win32         │
│                                     │
│ ❌ Files will NOT be uploaded for    │
│    security reasons.                │
│                                     │
│              [OK]                   │
└─────────────────────────────────────┘
```

**Actions:**
- Files are NOT uploaded to cloud
- USB drive can be safely removed
- Infected files logged for analysis
- Consider running full antivirus scan

## Monitoring and Status

### Checking Service Status

```bash
# Service status
sudo systemctl status pi-usb-safegate

# Detailed status with daemon information
sudo ./daemon-control.sh status

# Quick status check
python3 -c "from modules.status_manager import StatusManager; import json; print(json.dumps(StatusManager.read_status(), indent=2))"
```

### Viewing Logs

```bash
# View live logs
sudo journalctl -u pi-usb-safegate -f

# View recent logs
sudo journalctl -u pi-usb-safegate -n 50

# View logs with daemon control script
sudo ./daemon-control.sh logs
sudo ./daemon-control.sh logs-follow
```

### Status Information

The daemon provides real-time status information:

```json
{
  "daemon_status": "idle",
  "message": "Service started - monitoring for USB drives",
  "last_activity": "2024-01-15T10:30:45",
  "uptime": "2:15:30",
  "processing_count": 5,
  "errors": []
}
```

**Status Values:**
- `idle`: Waiting for USB drives
- `scanning`: Scanning files for malware
- `processing`: Creating ZIP archive
- `uploading`: Uploading to Nextcloud
- `error`: Error occurred
- `stopped`: Service not running

## Service Management

### Starting and Stopping

```bash
# Start service
sudo systemctl start pi-usb-safegate

# Stop service
sudo systemctl stop pi-usb-safegate

# Restart service
sudo systemctl restart pi-usb-safegate

# Reload configuration
sudo systemctl reload pi-usb-safegate
```

### Auto-Start Management

```bash
# Enable auto-start on boot
sudo systemctl enable pi-usb-safegate

# Disable auto-start
sudo systemctl disable pi-usb-safegate

# Check if enabled
sudo systemctl is-enabled pi-usb-safegate
```

### Service Dependencies

The service automatically handles dependencies:
- **ClamAV**: Must be running for malware scanning
- **Network**: Required for cloud upload and email
- **USB Subsystem**: Needed for device detection

## USB Drive Handling

### Supported Devices

- USB flash drives
- USB hard drives
- SD cards with USB adapters
- Multi-partition devices (first partition used)

### File Systems

- FAT32 (most common)
- NTFS
- exFAT
- ext4

### Device Requirements

- Must be automatically mounted by system
- Readable file system
- Available in `/media/` or `/mnt/`

### Multiple USB Drives

- Service processes one drive at a time
- Processing queue handles multiple insertions
- Each drive processed independently
- No interference between drives

## File Processing

### Supported File Types

All file types are supported, including:
- Documents (PDF, DOC, TXT)
- Images (JPG, PNG, GIF)
- Videos (MP4, AVI, MOV)
- Archives (ZIP, RAR, 7Z)
- Executables (with caution)

### File Size Limits

- Individual files: Up to 100MB (configurable)
- Total archive: Up to 1GB (configurable)
- Large files skipped with warning

### Exclusions

Default excluded files:
- System files (`.DS_Store`, `Thumbs.db`)
- Temporary files (`*.tmp`, `*.temp`)
- Hidden files (starting with `.`)
- Log files (`*.log`)

Configure exclusions in `config.ini`:
```ini
[PROCESSING]
exclude_patterns = *.tmp,*.log,Thumbs.db,.DS_Store
```

## Email Notifications

### Email Content

Professional HTML emails include:
- Download link to Nextcloud file
- File information (name, size, date)
- Security confirmation (malware scan passed)
- Expiration notice (7 days default)
- Instructions for download

### Delivery

- Emails sent via configured SMTP server
- TLS encryption used by default
- Delivery confirmed in logs
- Failed deliveries logged as errors

### Multiple Recipients

To send to multiple recipients:
1. Insert USB drive
2. Enter first email address
3. Re-insert USB drive
4. Enter second email address
5. Repeat as needed

## Error Handling

### Common Scenarios

1. **USB Drive Not Detected**
   - Check USB connection
   - Verify file system compatibility
   - Check mount permissions

2. **Malware Detected**
   - Files not uploaded (security)
   - Warning dialog displayed
   - Details logged for analysis

3. **Upload Failed**
   - Check network connectivity
   - Verify Nextcloud credentials
   - Check storage quota

4. **Email Failed**
   - Verify SMTP settings
   - Check email credentials
   - Confirm network access

### Recovery Actions

The service automatically:
- Retries failed operations
- Recovers from network interruptions
- Restarts after crashes
- Logs all error details

### Manual Recovery

```bash
# Restart service
sudo systemctl restart pi-usb-safegate

# Check configuration
sudo ./daemon-control.sh test

# View error logs
sudo journalctl -u pi-usb-safegate -p err

# Reset service state
sudo systemctl stop pi-usb-safegate
sudo rm -f /var/run/pi-usb-safegate/status.json
sudo systemctl start pi-usb-safegate
```

## Performance Considerations

### Processing Time

Typical processing times:
- Malware scan: 1-5 minutes (depends on file count/size)
- ZIP creation: 30 seconds to 2 minutes
- Upload: 1-10 minutes (depends on file size and network)
- Email delivery: 5-30 seconds

### Resource Usage

- **CPU**: Moderate during scanning, low during idle
- **Memory**: 50-200MB depending on file sizes
- **Storage**: Temporary files during processing
- **Network**: Upload bandwidth utilized

### Optimization Tips

1. **Faster Scanning**
   - Keep ClamAV database updated
   - Exclude unnecessary file types
   - Limit maximum file sizes

2. **Faster Uploads**
   - Use wired network connection
   - Check Nextcloud server performance
   - Consider file compression levels

3. **Reduced Resource Usage**
   - Lower ZIP compression level
   - Exclude large media files
   - Set processing limits

## Advanced Usage

### Multiple Configuration Profiles

Create different configurations for different use cases:

```bash
# Create profile-specific configs
sudo cp /etc/pi-usb-safegate/config.ini /etc/pi-usb-safegate/config-work.ini
sudo cp /etc/pi-usb-safegate/config.ini /etc/pi-usb-safegate/config-personal.ini

# Switch profiles
sudo ln -sf /etc/pi-usb-safegate/config-work.ini /etc/pi-usb-safegate/config.ini
sudo systemctl restart pi-usb-safegate
```

### Manual Processing

Process specific directories manually:

```bash
# Process a specific directory
sudo python3 -c "
from modules.file_processor import FileProcessor
from modules.nextcloud_uploader import NextcloudUploader
from modules.config_manager import ConfigManager

config = ConfigManager()
processor = FileProcessor()
uploader = NextcloudUploader(config)

# Create archive
files = ['/path/to/file1.txt', '/path/to/file2.pdf']
zip_path = processor.create_zip(files)

# Upload to Nextcloud
result = uploader.upload_file(zip_path)
print(f'Upload result: {result}')
"
```

### Scheduled Operations

Set up scheduled cleanup:

```bash
# Add to crontab
sudo crontab -e

# Add line for daily cleanup
0 2 * * * /usr/bin/python3 /usr/share/pi-usb-safegate/modules/cleanup_scheduler.py
```

### Remote Monitoring

Monitor service remotely:

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Check service status
sudo systemctl status pi-usb-safegate

# View recent activity
sudo journalctl -u pi-usb-safegate -n 20
```

## Troubleshooting Usage Issues

### Service Won't Start

```bash
# Check system dependencies
sudo systemctl status clamav-daemon
sudo systemctl status network-online.target

# Verify configuration
sudo python3 -c "from modules.config_manager import ConfigManager; ConfigManager()"

# Check permissions
ls -la /etc/pi-usb-safegate/
ls -la /var/log/pi-usb-safegate/
```

### USB Detection Issues

```bash
# Check USB devices
lsusb
lsblk

# Check mount points
df -h
mount | grep usb

# Test USB detection manually
sudo python3 -c "
from modules.usb_monitor import USBMonitor
monitor = USBMonitor(lambda x: print(f'Inserted: {x}'), lambda x: print(f'Removed: {x}'))
devices = monitor._get_usb_storage_devices()
print(f'Found devices: {devices}')
"
```

### Processing Stuck

```bash
# Check current status
sudo ./daemon-control.sh status

# View active processes
ps aux | grep python3

# Restart service if needed
sudo systemctl restart pi-usb-safegate
```

## Best Practices

### Regular Maintenance

1. **Update ClamAV Database**
   ```bash
   sudo freshclam
   ```

2. **Monitor Logs**
   ```bash
   sudo journalctl -u pi-usb-safegate -f
   ```

3. **Check Storage Space**
   ```bash
   df -h
   ```

4. **Test Configuration**
   ```bash
   sudo ./daemon-control.sh test
   ```

### Security Practices

1. **Regular Updates**
   - Keep Raspberry Pi OS updated
   - Update ClamAV regularly
   - Monitor security advisories

2. **Access Control**
   - Use strong passwords
   - Enable SSH key authentication
   - Disable unnecessary services

3. **Monitoring**
   - Review logs regularly
   - Monitor network traffic
   - Check file access logs

### Operational Practices

1. **Documentation**
   - Document configuration changes
   - Keep backup of working config
   - Record operational procedures

2. **Testing**
   - Test with known clean files
   - Verify email delivery
   - Test malware detection

3. **Backup**
   - Backup configuration files
   - Export Nextcloud data
   - Document email settings