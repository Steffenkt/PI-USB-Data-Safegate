"""
USB Monitor Module
Continuously monitors for USB device insertion and removal using udev
"""

import os
import logging
import threading
import time
import subprocess
import re
from typing import Callable, Dict, List, Optional


class USBMonitor:
    """Monitor USB devices using udev and polling"""
    
    def __init__(self, on_insert_callback: Callable, on_remove_callback: Callable):
        self.logger = logging.getLogger(__name__)
        self.on_insert_callback = on_insert_callback
        self.on_remove_callback = on_remove_callback
        
        self.running = False
        self.monitor_thread = None
        self.known_devices = set()
        self.device_info_cache = {}
        
        # Try to import pyudev for more efficient monitoring
        self.use_pyudev = self._try_import_pyudev()
        
    def _try_import_pyudev(self) -> bool:
        """Try to import pyudev for efficient USB monitoring"""
        try:
            import pyudev
            self.pyudev = pyudev
            self.logger.info("Using pyudev for USB monitoring")
            return True
        except ImportError:
            self.logger.info("pyudev not available, using polling method")
            return False
            
    def start(self):
        """Start USB monitoring"""
        if self.running:
            self.logger.warning("USB monitor is already running")
            return
            
        self.logger.info("Starting USB monitoring")
        self.running = True
        
        # Initial scan for existing devices
        self._scan_existing_devices()
        
        # Start monitoring thread
        if self.use_pyudev:
            self.monitor_thread = threading.Thread(target=self._monitor_with_pyudev, daemon=True)
        else:
            self.monitor_thread = threading.Thread(target=self._monitor_with_polling, daemon=True)
            
        self.monitor_thread.start()
        
    def stop(self):
        """Stop USB monitoring"""
        if not self.running:
            return
            
        self.logger.info("Stopping USB monitoring")
        self.running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
            
    def _scan_existing_devices(self):
        """Scan for existing USB storage devices"""
        try:
            devices = self._get_usb_storage_devices()
            self.known_devices = set(dev['device'] for dev in devices)
            
            for device in devices:
                self.device_info_cache[device['device']] = device
                
            self.logger.info(f"Found {len(devices)} existing USB storage devices")
            
        except Exception as e:
            self.logger.error(f"Error scanning existing devices: {e}")
            
    def _monitor_with_pyudev(self):
        """Monitor USB devices using pyudev"""
        try:
            context = self.pyudev.Context()
            monitor = self.pyudev.Monitor.from_netlink(context)
            monitor.filter_by(subsystem='block', device_type='partition')
            
            for device in iter(monitor.poll, None):
                if not self.running:
                    break
                    
                try:
                    if device.action == 'add':
                        self._handle_device_add(device)
                    elif device.action == 'remove':
                        self._handle_device_remove(device)
                        
                except Exception as e:
                    self.logger.error(f"Error handling device event: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error in pyudev monitoring: {e}")
            # Fall back to polling
            self._monitor_with_polling()
            
    def _monitor_with_polling(self):
        """Monitor USB devices using polling"""
        self.logger.info("Starting polling-based USB monitoring")
        
        while self.running:
            try:
                current_devices = self._get_usb_storage_devices()
                current_device_paths = set(dev['device'] for dev in current_devices)
                
                # Check for new devices
                new_devices = current_device_paths - self.known_devices
                for device_path in new_devices:
                    device_info = next((dev for dev in current_devices if dev['device'] == device_path), None)
                    if device_info:
                        self._device_inserted(device_info)
                        
                # Check for removed devices
                removed_devices = self.known_devices - current_device_paths
                for device_path in removed_devices:
                    if device_path in self.device_info_cache:
                        self._device_removed(self.device_info_cache[device_path])
                        del self.device_info_cache[device_path]
                        
                self.known_devices = current_device_paths
                
                # Update device info cache
                for device in current_devices:
                    self.device_info_cache[device['device']] = device
                    
            except Exception as e:
                self.logger.error(f"Error in polling monitor: {e}")
                
            time.sleep(2)  # Poll every 2 seconds
            
    def _handle_device_add(self, device):
        """Handle device addition from pyudev"""
        try:
            device_path = device.device_node
            if not device_path:
                return
                
            # Check if it's a USB storage device
            if self._is_usb_storage_device(device_path):
                device_info = self._get_device_info(device_path)
                if device_info:
                    self._device_inserted(device_info)
                    
        except Exception as e:
            self.logger.error(f"Error handling device add: {e}")
            
    def _handle_device_remove(self, device):
        """Handle device removal from pyudev"""
        try:
            device_path = device.device_node
            if not device_path:
                return
                
            if device_path in self.device_info_cache:
                device_info = self.device_info_cache[device_path]
                self._device_removed(device_info)
                del self.device_info_cache[device_path]
                
        except Exception as e:
            self.logger.error(f"Error handling device remove: {e}")
            
    def _device_inserted(self, device_info: Dict):
        """Handle device insertion"""
        self.logger.info(f"USB device inserted: {device_info['device']}")
        self.known_devices.add(device_info['device'])
        self.device_info_cache[device_info['device']] = device_info
        
        # Wait a moment for the device to be fully mounted
        time.sleep(1)
        
        # Verify device is still available and mounted
        if self._is_device_mounted(device_info['device']):
            self.on_insert_callback(device_info)
        else:
            self.logger.warning(f"Device {device_info['device']} not properly mounted")
            
    def _device_removed(self, device_info: Dict):
        """Handle device removal"""
        self.logger.info(f"USB device removed: {device_info['device']}")
        self.known_devices.discard(device_info['device'])
        self.on_remove_callback(device_info)
        
    def _get_usb_storage_devices(self) -> List[Dict]:
        """Get list of USB storage devices"""
        devices = []
        
        try:
            # Use lsblk to get block devices
            result = subprocess.run(['lsblk', '-o', 'NAME,SIZE,LABEL,MOUNTPOINT,TYPE,TRAN'], 
                                  capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 6:
                    name = parts[0].strip('├─└─│ ')
                    size = parts[1]
                    label = parts[2] if parts[2] != '' else 'Unlabeled'
                    mount_point = parts[3] if parts[3] != '' else None
                    device_type = parts[4]
                    transport = parts[5] if len(parts) > 5 else ''
                    
                    # Check if it's a USB storage device
                    if (device_type == 'part' and 
                        transport == 'usb' and 
                        mount_point and 
                        self._is_usb_storage_device(f'/dev/{name}')):
                        
                        device_info = {
                            'device': f'/dev/{name}',
                            'size': size,
                            'label': label,
                            'mount_point': mount_point,
                            'transport': transport
                        }
                        devices.append(device_info)
                        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error running lsblk: {e}")
        except Exception as e:
            self.logger.error(f"Error getting USB devices: {e}")
            
        return devices
        
    def _is_usb_storage_device(self, device_path: str) -> bool:
        """Check if a device is a USB storage device"""
        try:
            # Extract device name without partition number
            device_name = os.path.basename(device_path)
            base_device = re.sub(r'\d+$', '', device_name)
            
            # Check udev info for USB properties
            result = subprocess.run(['udevadm', 'info', '--query=property', 
                                   f'--name=/dev/{base_device}'],
                                  capture_output=True, text=True, check=True)
            
            properties = result.stdout.lower()
            
            # Check for USB properties
            return ('id_bus=usb' in properties or 
                   'id_usb_driver=usb-storage' in properties or
                   'devtype=disk' in properties)
                   
        except subprocess.CalledProcessError:
            return False
        except Exception as e:
            self.logger.error(f"Error checking if device is USB storage: {e}")
            return False
            
    def _get_device_info(self, device_path: str) -> Optional[Dict]:
        """Get detailed information about a device"""
        try:
            result = subprocess.run(['lsblk', '-o', 'SIZE,LABEL,MOUNTPOINT', device_path],
                                  capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                return {
                    'device': device_path,
                    'size': parts[0] if len(parts) > 0 else 'Unknown',
                    'label': parts[1] if len(parts) > 1 and parts[1] != '' else 'Unlabeled',
                    'mount_point': parts[2] if len(parts) > 2 and parts[2] != '' else None,
                    'transport': 'usb'
                }
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error getting device info for {device_path}: {e}")
        except Exception as e:
            self.logger.error(f"Error getting device info: {e}")
            
        return None
        
    def _is_device_mounted(self, device_path: str) -> bool:
        """Check if a device is properly mounted"""
        try:
            result = subprocess.run(['findmnt', device_path],
                                  capture_output=True, text=True, check=False)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error checking if device is mounted: {e}")
            return False
            
    def get_mounted_usb_devices(self) -> List[Dict]:
        """Get currently mounted USB devices"""
        return [info for info in self.device_info_cache.values() 
                if info.get('mount_point') and self._is_device_mounted(info['device'])]
                
    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        return self.running and self.monitor_thread and self.monitor_thread.is_alive()