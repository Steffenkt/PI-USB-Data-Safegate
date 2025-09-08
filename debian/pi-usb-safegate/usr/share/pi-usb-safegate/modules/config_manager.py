"""
Configuration Manager Module
Handles reading and managing application configuration
"""

import configparser
import os
import logging


class ConfigManager:
    def __init__(self, config_file=None):
        if config_file is None:
            # Try system config first, then local config
            system_config = '/etc/pi-usb-safegate/config.ini'
            local_config = 'config.ini'
            
            if os.path.exists(system_config):
                self.config_file = system_config
            elif os.path.exists(local_config):
                self.config_file = local_config
            else:
                self.config_file = 'config.ini'
        else:
            self.config_file = config_file
            
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(__name__)
        self.load_config()
        
    def load_config(self):
        if not os.path.exists(self.config_file):
            self.logger.error(f"Configuration file {self.config_file} not found!")
            raise FileNotFoundError(f"Configuration file {self.config_file} not found")
            
        try:
            self.config.read(self.config_file)
            self.logger.info(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error reading configuration: {str(e)}")
            raise
            
    def get_email_config(self):
        return {
            'smtp_server': self.config.get('EMAIL', 'smtp_server'),
            'smtp_port': self.config.getint('EMAIL', 'smtp_port'),
            'smtp_username': self.config.get('EMAIL', 'smtp_username'),
            'smtp_password': self.config.get('EMAIL', 'smtp_password'),
            'sender_name': self.config.get('EMAIL', 'sender_name')
        }
        
    def get_cloud_config(self):
        provider = self.config.get('CLOUD_STORAGE', 'provider')
        
        if provider == 'nextcloud':
            return {
                'provider': 'nextcloud',
                'url': self.config.get('NEXTCLOUD', 'url'),
                'username': self.config.get('NEXTCLOUD', 'username'),
                'password': self.config.get('NEXTCLOUD', 'password'),
                'upload_path': self.config.get('NEXTCLOUD', 'upload_path')
            }
        else:
            raise ValueError(f"Unsupported cloud provider: {provider}")
    
    def get_nextcloud_config(self):
        """Get Nextcloud-specific configuration"""
        return {
            'url': self.config.get('NEXTCLOUD', 'url'),
            'username': self.config.get('NEXTCLOUD', 'username'),
            'password': self.config.get('NEXTCLOUD', 'password'),
            'upload_path': self.config.get('NEXTCLOUD', 'upload_path')
        }
            
    def get_security_config(self):
        return {
            'clamav_db_path': self.config.get('SECURITY', 'clamav_db_path'),
            'max_file_size_mb': self.config.getint('SECURITY', 'max_file_size_mb'),
            'quarantine_infected': self.config.getboolean('SECURITY', 'quarantine_infected')
        }
        
    def get_cleanup_config(self):
        return {
            'auto_delete_days': self.config.getint('CLEANUP', 'auto_delete_days'),
            'cleanup_check_interval_hours': self.config.getint('CLEANUP', 'cleanup_check_interval_hours')
        }
        
    def get_logging_config(self):
        return {
            'log_level': self.config.get('LOGGING', 'log_level'),
            'log_file': self.config.get('LOGGING', 'log_file'),
            'max_log_size_mb': self.config.getint('LOGGING', 'max_log_size_mb')
        }