# PI USB Data Safegate Installation Guide

## Quick Installation

### Option 1: Using the Debian Package (Recommended)

1. Download the package file: `pi-usb-safegate_1.0.1_all.deb`

2. Install the package:
   ```bash
   sudo dpkg -i pi-usb-safegate_1.0.1_all.deb
   ```

3. If there are dependency issues, fix them:
   ```bash
   sudo apt --fix-broken install
   ```

4. Configure the application:
   ```bash
   sudo pi-usb-safegate-setup
   ```

5. Run the application:
   ```bash
   sudo pi-usb-safegate
   ```

### Option 2: Using the Install Script

1. Make the install script executable:
   ```bash
   chmod +x install.sh
   ```

2. Run the installer:
   ```bash
   sudo ./install.sh
   ```

## Post-Installation

- Configuration file: `/etc/pi-usb-safegate/config.ini`
- Log files: `/var/log/pi-usb-safegate/`
- Application files: `/usr/share/pi-usb-safegate/`

## Uninstallation

To remove the application:
```bash
sudo apt remove pi-usb-safegate
```

To remove all configuration files:
```bash
sudo apt purge pi-usb-safegate
```

## Troubleshooting

### Common Issues

1. **Permission denied**: Make sure to run with sudo
2. **Missing dependencies**: Run `sudo apt --fix-broken install`
3. **ClamAV not working**: Run `sudo freshclam` to update virus database

### Getting Help

Check the application logs at `/var/log/pi-usb-safegate/safegate.log`
