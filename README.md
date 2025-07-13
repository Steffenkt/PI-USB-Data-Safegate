# PI USB Data Safegate

A secure, user-friendly application for Raspberry Pi that allows users to safely transfer data from USB drives to cloud storage providers. The application scans all files for malware before uploading and provides email notifications with download links.

## Features

- 🔒 **Malware Scanning**: Uses ClamAV to scan all files for viruses and malware
- 📁 **USB Drive Detection**: Automatically detects and lists connected USB drives
- ☁️ **Cloud Storage**: Supports Nextcloud and Dropbox for file uploads
- 📧 **Email Notifications**: Sends professional HTML emails with download links
- 🗂️ **File Compression**: Zips safe files for efficient transfer
- 🗑️ **Automatic Cleanup**: Deletes uploaded files after 7 days (configurable)
- 📊 **Real-time Status**: Shows progress and status updates in the GUI
- 🔐 **Security First**: Only uploads files that pass malware scanning

## Requirements

### System Requirements
- Raspberry Pi running Raspberry Pi OS (Debian-based Linux)
- Python 3.7 or higher
- Root privileges (for USB device access)
- Internet connection for cloud uploads and email

### Software Dependencies
- ClamAV antivirus software
- Python packages (see requirements.txt)

## Installation

### 1. Install System Dependencies

```bash
# Update package list
sudo apt update

# Install ClamAV
sudo apt install clamav clamav-daemon clamav-freshclam

# Install Python dependencies
sudo apt install python3-pip python3-tkinter

# Update ClamAV virus database
sudo freshclam
```

### 2. Install Python Dependencies

```bash
# Install required Python packages
pip3 install -r src/pi_usb_safegate/requirements.txt
```

### 3. Configure the Application

1. Edit the `config.ini` file with your settings:

```ini
[EMAIL]
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_username = your_email@gmail.com
smtp_password = your_app_password
sender_name = PI USB Data Safegate

[CLOUD_STORAGE]
provider = nextcloud
nextcloud_url = https://your-nextcloud.com
nextcloud_username = your_username
nextcloud_password = your_password
nextcloud_upload_path = /USB_Transfers

[SECURITY]
clamav_db_path = /var/lib/clamav
max_file_size_mb = 100
quarantine_infected = true

[CLEANUP]
auto_delete_days = 7
cleanup_check_interval_hours = 24
```

### 4. Set Up Email Authentication

For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an app password
3. Use the app password in the config file

### 5. Set Up Cloud Storage

#### For Nextcloud:
- Create a user account
- Set up application password (recommended)
- Create the upload directory

#### For Dropbox:
- Create a Dropbox app at https://www.dropbox.com/developers/apps
- Generate an access token
- Add the token to the config file

## Usage

### 1. Start the Application

```bash
# Run with root privileges (required for USB access)
sudo python3 main.py
```

### 2. Using the GUI

1. **Select USB Drive**: Choose from detected USB drives in the dropdown
2. **Enter Email**: Provide your email address for notifications
3. **Click "Scan and Upload"**: Start the process
4. **Monitor Progress**: Watch real-time status updates
5. **Check Email**: Receive download link when complete

### 3. Process Flow

1. **USB Detection**: Application scans for connected USB drives
2. **Malware Scanning**: ClamAV scans all files on the selected drive
3. **File Processing**: Safe files are zipped for transfer
4. **Cloud Upload**: Zip file is uploaded to configured cloud storage
5. **Email Notification**: Download link is sent to user's email
6. **Automatic Cleanup**: Files are deleted after 7 days

## Security Features

- **Malware Detection**: All files are scanned before upload
- **Quarantine System**: Infected files are isolated
- **Secure Transfer**: Files are compressed and uploaded via HTTPS
- **Automatic Cleanup**: No files remain permanently on cloud storage
- **Access Control**: Requires root privileges for USB access

## Configuration Options

### Email Settings
- **smtp_server**: SMTP server address
- **smtp_port**: SMTP port (usually 587 for TLS)
- **smtp_username**: Email account username
- **smtp_password**: Email account password or app password
- **sender_name**: Display name for outgoing emails

### Cloud Storage Settings
- **provider**: Choose 'nextcloud' or 'dropbox'
- **nextcloud_url**: Full URL to your Nextcloud instance
- **nextcloud_username**: Nextcloud username
- **nextcloud_password**: Nextcloud password
- **nextcloud_upload_path**: Directory for uploads
- **dropbox_access_token**: Dropbox API access token

### Security Settings
- **clamav_db_path**: Path to ClamAV virus database
- **max_file_size_mb**: Maximum file size to scan (MB)
- **quarantine_infected**: Whether to quarantine infected files

### Cleanup Settings
- **auto_delete_days**: Days before automatic deletion
- **cleanup_check_interval_hours**: How often to check for cleanup

## Troubleshooting

### Common Issues

1. **"ClamAV not found"**
   ```bash
   sudo apt install clamav clamav-daemon
   sudo freshclam
   ```

2. **"Permission denied" for USB**
   ```bash
   sudo python3 main.py
   ```

3. **"No USB drives found"**
   - Ensure USB drive is properly connected
   - Check if drive is mounted: `lsblk`
   - Try different USB port

4. **Email sending fails**
   - Check email credentials in config.ini
   - Verify SMTP settings
   - For Gmail, use app password instead of regular password

5. **Cloud upload fails**
   - Verify cloud storage credentials
   - Check internet connection
   - Ensure upload directory exists

### Log Files

The application creates detailed logs in `safegate.log`:
- Startup and shutdown events
- USB drive detection
- Malware scan results
- Upload progress
- Email notifications
- Error messages

### Testing Connections

You can test your configuration by checking the log files after startup. The application will test:
- ClamAV availability
- Email server connection
- Cloud storage access

## File Structure

```
PI-USB-Data-Safegate/
├── main.py                     # Main application entry point
├── config.ini                  # Configuration file
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── modules/
│   ├── __init__.py
│   ├── config_manager.py       # Configuration management
│   ├── usb_detector.py         # USB drive detection
│   ├── malware_scanner.py      # ClamAV integration
│   ├── file_processor.py       # File handling and zipping
│   ├── cloud_uploader.py       # Cloud storage uploads
│   ├── email_notifier.py       # Email notifications
│   └── cleanup_scheduler.py    # Automatic file cleanup
├── safegate.log                # Application log file (created at runtime)
└── cleanup_schedule.json       # Cleanup schedule database (created at runtime)
```

## Security Considerations

1. **Root Privileges**: Required for USB device access
2. **Malware Scanning**: All files are scanned before upload
3. **Credential Security**: Store sensitive credentials securely
4. **Network Security**: Use HTTPS for all cloud communications
5. **Temporary Files**: Cleaned up after processing
6. **Automatic Deletion**: Files don't remain permanently in cloud storage

## Support

For issues and support:
1. Check the troubleshooting section
2. Review log files for error messages
3. Verify configuration settings
4. Ensure all dependencies are installed

## License

This project is designed for educational and security purposes. Use responsibly and in accordance with your organization's security policies.

## Contributing

When contributing to this project, please ensure:
- All security features remain intact
- Malware scanning is never bypassed
- Code follows Python best practices
- Documentation is updated accordingly