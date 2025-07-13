# Configuration Guide

This document provides comprehensive configuration options for the Secure Nextcloud USB Uploader.

## Configuration File Location

The main configuration file is located at:
- **System Installation**: `/etc/pi-usb-safegate/config.ini`
- **Development**: `config.ini` in project root

## Configuration Sections

### [NEXTCLOUD]

Nextcloud server connection and upload settings.

```ini
[NEXTCLOUD]
url = https://your-nextcloud.com
username = your_username
password = your_app_password
upload_path = /USB_Transfers
```

#### Parameters

- **`url`** (required)
  - Your Nextcloud server URL
  - Must include protocol (https://)
  - Example: `https://cloud.example.com`

- **`username`** (required)
  - Your Nextcloud username
  - Example: `myuser`

- **`password`** (required)
  - Nextcloud app password (recommended) or account password
  - Generate app password: Settings → Security → Devices & sessions
  - Example: `xxxxx-xxxxx-xxxxx-xxxxx-xxxxx`

- **`upload_path`** (required)
  - Directory path on Nextcloud for uploads
  - Will be created if it doesn't exist
  - Example: `/USB_Transfers`, `/Uploads/USB`

### [EMAIL]

Email notification settings for sending download links.

```ini
[EMAIL]
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_username = your_email@gmail.com
smtp_password = your_app_password
sender_name = PI USB Data Safegate
use_tls = true
use_ssl = false
```

#### Parameters

- **`smtp_server`** (required)
  - SMTP server hostname
  - Examples: `smtp.gmail.com`, `smtp.outlook.com`, `mail.example.com`

- **`smtp_port`** (required)
  - SMTP server port
  - Common ports: `587` (TLS), `465` (SSL), `25` (unencrypted)

- **`smtp_username`** (required)
  - Email account username (usually email address)
  - Example: `user@gmail.com`

- **`smtp_password`** (required)
  - Email account password or app password
  - For Gmail: Use app password instead of account password
  - Example: `xxxxxxxxxxxxxxxx`

- **`sender_name`** (optional)
  - Display name for outgoing emails
  - Default: `PI USB Data Safegate`

- **`use_tls`** (optional)
  - Enable TLS encryption
  - Default: `true`
  - Recommended for port 587

- **`use_ssl`** (optional)
  - Enable SSL encryption
  - Default: `false`
  - Use for port 465

### [SECURITY]

Security and malware scanning settings.

```ini
[SECURITY]
clamav_db_path = /var/lib/clamav
max_file_size_mb = 100
quarantine_infected = true
scan_archives = true
scan_timeout = 300
```

#### Parameters

- **`clamav_db_path`** (required)
  - Path to ClamAV virus database
  - Default: `/var/lib/clamav`

- **`max_file_size_mb`** (optional)
  - Maximum file size to scan (in MB)
  - Default: `100`
  - Files larger than this are skipped

- **`quarantine_infected`** (optional)
  - Quarantine infected files instead of just skipping
  - Default: `true`

- **`scan_archives`** (optional)
  - Scan inside archive files (ZIP, RAR, etc.)
  - Default: `true`

- **`scan_timeout`** (optional)
  - Timeout for scanning individual files (seconds)
  - Default: `300` (5 minutes)

### [CLEANUP]

Automatic file cleanup settings.

```ini
[CLEANUP]
auto_delete_days = 7
cleanup_check_interval_hours = 24
keep_local_copies = false
cleanup_on_startup = true
```

#### Parameters

- **`auto_delete_days`** (required)
  - Days to keep files before automatic deletion
  - Default: `7`
  - Set to `0` to disable automatic cleanup

- **`cleanup_check_interval_hours`** (optional)
  - How often to check for files to clean up (hours)
  - Default: `24`

- **`keep_local_copies`** (optional)
  - Keep local ZIP files after upload
  - Default: `false`

- **`cleanup_on_startup`** (optional)
  - Clean up old files when daemon starts
  - Default: `true`

### [LOGGING]

Logging configuration.

```ini
[LOGGING]
log_level = INFO
log_file = /var/log/pi-usb-safegate/daemon.log
max_log_size_mb = 10
backup_count = 5
```

#### Parameters

- **`log_level`** (optional)
  - Logging level
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
  - Default: `INFO`

- **`log_file`** (optional)
  - Path to log file
  - Default: `/var/log/pi-usb-safegate/daemon.log`

- **`max_log_size_mb`** (optional)
  - Maximum log file size before rotation (MB)
  - Default: `10`

- **`backup_count`** (optional)
  - Number of backup log files to keep
  - Default: `5`

### [USB]

USB device monitoring settings.

```ini
[USB]
monitor_method = auto
poll_interval = 2
auto_mount = true
mount_timeout = 10
```

#### Parameters

- **`monitor_method`** (optional)
  - USB monitoring method
  - Options: `auto`, `pyudev`, `polling`
  - Default: `auto` (use pyudev if available, else polling)

- **`poll_interval`** (optional)
  - Polling interval in seconds (when using polling method)
  - Default: `2`

- **`auto_mount`** (optional)
  - Automatically mount USB drives if needed
  - Default: `true`

- **`mount_timeout`** (optional)
  - Timeout for mount operations (seconds)
  - Default: `10`

### [PROCESSING]

File processing settings.

```ini
[PROCESSING]
zip_compression_level = 6
include_hidden_files = false
max_archive_size_mb = 1000
exclude_patterns = *.tmp,*.log,Thumbs.db,.DS_Store
```

#### Parameters

- **`zip_compression_level`** (optional)
  - ZIP compression level (0-9)
  - 0 = no compression, 9 = maximum compression
  - Default: `6`

- **`include_hidden_files`** (optional)
  - Include hidden files in archive
  - Default: `false`

- **`max_archive_size_mb`** (optional)
  - Maximum archive size (MB)
  - Default: `1000`

- **`exclude_patterns`** (optional)
  - Comma-separated list of file patterns to exclude
  - Supports wildcards
  - Default: `*.tmp,*.log,Thumbs.db,.DS_Store`

## Common Configuration Examples

### Gmail Configuration
```ini
[EMAIL]
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_username = your_email@gmail.com
smtp_password = your_gmail_app_password
sender_name = PI USB Safegate
use_tls = true
```

### Outlook/Hotmail Configuration
```ini
[EMAIL]
smtp_server = smtp.live.com
smtp_port = 587
smtp_username = your_email@outlook.com
smtp_password = your_outlook_password
sender_name = PI USB Safegate
use_tls = true
```

### Self-Hosted Email Server
```ini
[EMAIL]
smtp_server = mail.yourdomain.com
smtp_port = 587
smtp_username = user@yourdomain.com
smtp_password = your_password
sender_name = PI USB Safegate
use_tls = true
```

### High-Security Configuration
```ini
[SECURITY]
max_file_size_mb = 50
quarantine_infected = true
scan_archives = true
scan_timeout = 600

[CLEANUP]
auto_delete_days = 3
cleanup_check_interval_hours = 6
keep_local_copies = false
```

### Development Configuration
```ini
[LOGGING]
log_level = DEBUG
max_log_size_mb = 50
backup_count = 10

[PROCESSING]
zip_compression_level = 1
include_hidden_files = true
```

## Environment Variables

Some settings can be overridden with environment variables:

- `NEXTCLOUD_URL`: Override Nextcloud URL
- `NEXTCLOUD_USER`: Override Nextcloud username
- `NEXTCLOUD_PASS`: Override Nextcloud password
- `EMAIL_SMTP_SERVER`: Override SMTP server
- `EMAIL_SMTP_USER`: Override SMTP username
- `EMAIL_SMTP_PASS`: Override SMTP password
- `LOG_LEVEL`: Override log level

Example:
```bash
export NEXTCLOUD_URL=https://cloud.example.com
export LOG_LEVEL=DEBUG
sudo systemctl restart pi-usb-safegate
```

## Configuration Validation

### Test Configuration
```bash
# Test all settings
sudo python3 /usr/share/pi-usb-safegate/daemon.py test

# Test specific components
python3 -c "from modules.nextcloud_uploader import NextcloudUploader; from modules.config_manager import ConfigManager; uploader = NextcloudUploader(ConfigManager()); print(uploader.test_connection())"
```

### Validate Email Settings
```bash
python3 -c "from modules.email_notifier import EmailNotifier; from modules.config_manager import ConfigManager; notifier = EmailNotifier(ConfigManager()); print(notifier.test_email_connection())"
```

### Check ClamAV
```bash
sudo systemctl status clamav-daemon
sudo freshclam
```

## Security Best Practices

### Nextcloud Security
- Use app passwords instead of account passwords
- Enable two-factor authentication on Nextcloud
- Use HTTPS for Nextcloud server
- Regularly update Nextcloud server
- Monitor access logs

### Email Security
- Use app passwords for Gmail/Outlook
- Enable two-factor authentication
- Use TLS/SSL encryption
- Monitor email account activity

### System Security
- Keep ClamAV database updated
- Regularly update Raspberry Pi OS
- Use strong passwords
- Enable firewall if needed
- Monitor system logs

### Configuration File Security
```bash
# Secure configuration file
sudo chmod 640 /etc/pi-usb-safegate/config.ini
sudo chown root:root /etc/pi-usb-safegate/config.ini

# Backup configuration
sudo cp /etc/pi-usb-safegate/config.ini /etc/pi-usb-safegate/config.ini.backup
```

## Troubleshooting Configuration

### Common Issues

1. **Invalid Nextcloud URL**
   - Ensure URL includes protocol (https://)
   - Check for typos in domain name
   - Verify server is accessible

2. **Authentication Failures**
   - Use app passwords instead of account passwords
   - Check username/password for typos
   - Verify account has necessary permissions

3. **Email Not Sending**
   - Check SMTP server settings
   - Verify port and encryption settings
   - Test with email client first

4. **ClamAV Errors**
   - Check ClamAV service status
   - Update virus database
   - Verify database path exists

### Configuration Testing
```bash
# Test individual components
sudo ./daemon-control.sh test

# Check logs for errors
sudo journalctl -u pi-usb-safegate -f

# Validate configuration syntax
python3 -c "from modules.config_manager import ConfigManager; ConfigManager()"
```

## Advanced Configuration

### Custom Upload Paths
```ini
[NEXTCLOUD]
upload_path = /USB_Transfers/%(hostname)s/%(date)s
```

Variables available:
- `%(hostname)s`: System hostname
- `%(date)s`: Current date (YYYY-MM-DD)
- `%(time)s`: Current time (HH-MM-SS)

### Multiple Email Recipients
```ini
[EMAIL]
# Use comma-separated list
smtp_recipients = admin@example.com,user@example.com
```

### Custom File Patterns
```ini
[PROCESSING]
exclude_patterns = *.tmp,*.log,*.bak,~*,#*,*.swp
include_patterns = *.pdf,*.doc,*.docx,*.jpg,*.png
```

## Configuration Migration

### Upgrading Configuration
When upgrading the application, your configuration file is preserved. New options are added with default values.

### Backup and Restore
```bash
# Backup configuration
sudo cp /etc/pi-usb-safegate/config.ini ~/config-backup.ini

# Restore configuration
sudo cp ~/config-backup.ini /etc/pi-usb-safegate/config.ini
sudo systemctl restart pi-usb-safegate
```

### Reset to Defaults
```bash
# Reset configuration to defaults
sudo cp /etc/pi-usb-safegate/config.ini.template /etc/pi-usb-safegate/config.ini
sudo systemctl restart pi-usb-safegate
```