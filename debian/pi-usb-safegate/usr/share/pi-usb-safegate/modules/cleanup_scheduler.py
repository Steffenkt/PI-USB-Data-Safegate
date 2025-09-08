"""
Cleanup Scheduler Module
Handles automatic deletion of uploaded files after specified time
"""

import os
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path


class CleanupScheduler:
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.cleanup_config = self.config.get_cleanup_config()
        self.cleanup_db_path = "cleanup_schedule.json"
        self.running = False
        self.cleanup_thread = None
        
        self.load_cleanup_schedule()
        self.start_cleanup_daemon()
        
    def load_cleanup_schedule(self):
        if os.path.exists(self.cleanup_db_path):
            try:
                with open(self.cleanup_db_path, 'r') as f:
                    self.cleanup_schedule = json.load(f)
                    
                for item in self.cleanup_schedule:
                    item['upload_time'] = datetime.fromisoformat(item['upload_time'])
                    
            except Exception as e:
                self.logger.error(f"Error loading cleanup schedule: {str(e)}")
                self.cleanup_schedule = []
        else:
            self.cleanup_schedule = []
            
    def save_cleanup_schedule(self):
        try:
            schedule_data = []
            for item in self.cleanup_schedule:
                schedule_item = item.copy()
                schedule_item['upload_time'] = item['upload_time'].isoformat()
                schedule_data.append(schedule_item)
                
            with open(self.cleanup_db_path, 'w') as f:
                json.dump(schedule_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving cleanup schedule: {str(e)}")
            
    def schedule_deletion(self, file_path, download_link, upload_time=None):
        if upload_time is None:
            upload_time = datetime.now()
            
        cleanup_item = {
            'file_path': file_path,
            'download_link': download_link,
            'upload_time': upload_time,
            'filename': os.path.basename(file_path),
            'delete_after_days': self.cleanup_config['auto_delete_days']
        }
        
        self.cleanup_schedule.append(cleanup_item)
        self.save_cleanup_schedule()
        
        self.logger.info(f"Scheduled cleanup for {file_path} in {self.cleanup_config['auto_delete_days']} days")
        
    def start_cleanup_daemon(self):
        if not self.running:
            self.running = True
            self.cleanup_thread = threading.Thread(target=self._cleanup_daemon, daemon=True)
            self.cleanup_thread.start()
            self.logger.info("Cleanup daemon started")
            
    def stop_cleanup_daemon(self):
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
            self.logger.info("Cleanup daemon stopped")
            
    def _cleanup_daemon(self):
        while self.running:
            try:
                self.check_and_cleanup()
                
                sleep_time = self.cleanup_config['cleanup_check_interval_hours'] * 3600
                
                for _ in range(int(sleep_time)):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Error in cleanup daemon: {str(e)}")
                time.sleep(60)
                
    def check_and_cleanup(self):
        current_time = datetime.now()
        items_to_remove = []
        
        for item in self.cleanup_schedule:
            days_since_upload = (current_time - item['upload_time']).days
            
            if days_since_upload >= item['delete_after_days']:
                success = self.delete_file(item)
                
                if success:
                    items_to_remove.append(item)
                    self.logger.info(f"Cleaned up expired file: {item['filename']}")
                else:
                    self.logger.warning(f"Failed to clean up file: {item['filename']}")
                    
        for item in items_to_remove:
            self.cleanup_schedule.remove(item)
            
        if items_to_remove:
            self.save_cleanup_schedule()
            
    def delete_file(self, cleanup_item):
        success = True
        
        try:
            if os.path.exists(cleanup_item['file_path']):
                os.remove(cleanup_item['file_path'])
                self.logger.info(f"Deleted local file: {cleanup_item['file_path']}")
                
        except Exception as e:
            self.logger.error(f"Error deleting local file: {str(e)}")
            success = False
            
        try:
            from .cloud_uploader import CloudUploader
            uploader = CloudUploader(self.config)
            cloud_deleted = uploader.delete_file(cleanup_item['filename'])
            
            if cloud_deleted:
                self.logger.info(f"Deleted cloud file: {cleanup_item['filename']}")
            else:
                self.logger.warning(f"Failed to delete cloud file: {cleanup_item['filename']}")
                success = False
                
        except Exception as e:
            self.logger.error(f"Error deleting cloud file: {str(e)}")
            success = False
            
        return success
        
    def get_cleanup_status(self):
        current_time = datetime.now()
        status = {
            'total_scheduled': len(self.cleanup_schedule),
            'pending_cleanup': [],
            'expired_items': []
        }
        
        for item in self.cleanup_schedule:
            days_since_upload = (current_time - item['upload_time']).days
            days_until_deletion = item['delete_after_days'] - days_since_upload
            
            item_status = {
                'filename': item['filename'],
                'upload_time': item['upload_time'].strftime('%Y-%m-%d %H:%M:%S'),
                'days_since_upload': days_since_upload,
                'days_until_deletion': days_until_deletion
            }
            
            if days_until_deletion <= 0:
                status['expired_items'].append(item_status)
            else:
                status['pending_cleanup'].append(item_status)
                
        return status
        
    def force_cleanup(self, filename=None):
        if filename:
            items_to_cleanup = [item for item in self.cleanup_schedule if item['filename'] == filename]
        else:
            items_to_cleanup = self.cleanup_schedule.copy()
            
        cleaned_count = 0
        
        for item in items_to_cleanup:
            success = self.delete_file(item)
            
            if success:
                self.cleanup_schedule.remove(item)
                cleaned_count += 1
                
        if cleaned_count > 0:
            self.save_cleanup_schedule()
            
        self.logger.info(f"Force cleanup completed: {cleaned_count} files cleaned")
        return cleaned_count
        
    def remove_from_schedule(self, filename):
        items_to_remove = [item for item in self.cleanup_schedule if item['filename'] == filename]
        
        for item in items_to_remove:
            self.cleanup_schedule.remove(item)
            
        if items_to_remove:
            self.save_cleanup_schedule()
            self.logger.info(f"Removed {filename} from cleanup schedule")
            return True
            
        return False
        
    def add_manual_cleanup(self, file_path, download_link, delete_after_days=None):
        if delete_after_days is None:
            delete_after_days = self.cleanup_config['auto_delete_days']
            
        cleanup_item = {
            'file_path': file_path,
            'download_link': download_link,
            'upload_time': datetime.now(),
            'filename': os.path.basename(file_path),
            'delete_after_days': delete_after_days
        }
        
        self.cleanup_schedule.append(cleanup_item)
        self.save_cleanup_schedule()
        
        self.logger.info(f"Added manual cleanup for {file_path} in {delete_after_days} days")
        
    def __del__(self):
        self.stop_cleanup_daemon()