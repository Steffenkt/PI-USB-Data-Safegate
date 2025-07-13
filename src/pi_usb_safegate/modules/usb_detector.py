"""
USB Drive Detection Module
Detects and lists connected USB drives on Linux systems
"""

import os
import subprocess
import logging
import re


class USBDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_usb_drives(self):
        usb_drives = []
        
        try:
            result = subprocess.run(['lsblk', '-o', 'NAME,SIZE,LABEL,MOUNTPOINT,TYPE'], 
                                  capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\n')[1:]
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 5 and parts[4] == 'part':
                    device_name = parts[0].strip('├─└─│ ')
                    size = parts[1]
                    label = parts[2] if parts[2] != '' else 'Unlabeled'
                    mountpoint = parts[3] if parts[3] != '' else None
                    
                    if self._is_usb_device(device_name) and mountpoint:
                        usb_drives.append({
                            'device': f'/dev/{device_name}',
                            'size': size,
                            'label': label,
                            'mountpoint': mountpoint
                        })
                        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error running lsblk: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error detecting USB drives: {str(e)}")
            
        self.logger.info(f"Found {len(usb_drives)} USB drives")
        return usb_drives
        
    def _is_usb_device(self, device_name):
        try:
            base_device = re.sub(r'\d+$', '', device_name)
            
            result = subprocess.run(['udevadm', 'info', '--query=property', 
                                   f'--name=/dev/{base_device}'],
                                  capture_output=True, text=True, check=True)
            
            properties = result.stdout
            
            return ('ID_BUS=usb' in properties or 
                   'ID_USB_DRIVER=usb-storage' in properties or
                   'DEVTYPE=disk' in properties and 'removable' in properties)
                   
        except subprocess.CalledProcessError:
            return False
        except Exception as e:
            self.logger.error(f"Error checking if device is USB: {str(e)}")
            return False
            
    def get_drive_info(self, device_path):
        try:
            result = subprocess.run(['lsblk', '-o', 'SIZE,LABEL,FSTYPE', device_path],
                                  capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                return {
                    'size': parts[0] if len(parts) > 0 else 'Unknown',
                    'label': parts[1] if len(parts) > 1 and parts[1] != '' else 'Unlabeled',
                    'filesystem': parts[2] if len(parts) > 2 else 'Unknown'
                }
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error getting drive info for {device_path}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error getting drive info: {str(e)}")
            
        return None
        
    def mount_drive(self, device_path, mount_point=None):
        if not mount_point:
            mount_point = f"/mnt/usb_{os.path.basename(device_path)}"
            
        try:
            os.makedirs(mount_point, exist_ok=True)
            
            result = subprocess.run(['mount', device_path, mount_point],
                                  capture_output=True, text=True, check=True)
            
            self.logger.info(f"Mounted {device_path} to {mount_point}")
            return mount_point
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error mounting {device_path}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error mounting drive: {str(e)}")
            return None
            
    def unmount_drive(self, mount_point):
        try:
            result = subprocess.run(['umount', mount_point],
                                  capture_output=True, text=True, check=True)
            
            self.logger.info(f"Unmounted {mount_point}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error unmounting {mount_point}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error unmounting drive: {str(e)}")
            return False