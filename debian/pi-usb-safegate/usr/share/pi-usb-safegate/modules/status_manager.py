"""
Status Manager Module
Manages daemon status and provides inter-process communication
"""

import os
import json
import logging
import threading
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path


class StatusManager:
    """Manages daemon status and provides status information"""
    
    def __init__(self, status_file: str = '/var/run/pi-usb-safegate/status.json'):
        self.logger = logging.getLogger(__name__)
        self.status_file = Path(status_file)
        self.lock = threading.Lock()
        
        # Ensure status directory exists
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize status
        self.current_status = {
            'daemon_status': 'stopped',
            'last_activity': None,
            'message': 'Service not started',
            'processing_count': 0,
            'errors': [],
            'uptime': None
        }
        
        self.start_time = datetime.now()
        self._save_status()
        
    def set_status(self, message: str, status: str = 'active'):
        """Set current status with message"""
        with self.lock:
            self.current_status.update({
                'daemon_status': status,
                'message': message,
                'last_activity': datetime.now().isoformat(),
                'uptime': str(datetime.now() - self.start_time)
            })
            
            self.logger.info(f"Status updated: {status} - {message}")
            self._save_status()
            
    def add_error(self, error_message: str):
        """Add an error to the status"""
        with self.lock:
            error_entry = {
                'timestamp': datetime.now().isoformat(),
                'message': error_message
            }
            
            self.current_status['errors'].append(error_entry)
            
            # Keep only last 10 errors
            if len(self.current_status['errors']) > 10:
                self.current_status['errors'] = self.current_status['errors'][-10:]
                
            self._save_status()
            
    def increment_processing_count(self):
        """Increment the processing counter"""
        with self.lock:
            self.current_status['processing_count'] += 1
            self._save_status()
            
    def get_status(self) -> Dict:
        """Get current status"""
        with self.lock:
            return self.current_status.copy()
            
    def _save_status(self):
        """Save status to file"""
        try:
            with open(self.status_file, 'w') as f:
                json.dump(self.current_status, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving status: {e}")
            
    @staticmethod
    def read_status(status_file: str = '/var/run/pi-usb-safegate/status.json') -> Optional[Dict]:
        """Read status from file (static method for external access)"""
        try:
            with open(status_file, 'r') as f:
                return json.load(f)
                
        except FileNotFoundError:
            return None
        except Exception as e:
            return {'error': f'Error reading status: {e}'}
            
    def cleanup(self):
        """Clean up status file"""
        try:
            if self.status_file.exists():
                self.status_file.unlink()
                
        except Exception as e:
            self.logger.error(f"Error cleaning up status file: {e}")