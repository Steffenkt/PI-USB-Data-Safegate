"""
File Processor Module
Handles file operations like zipping safe files
"""

import os
import zipfile
import logging
import tempfile
from datetime import datetime
from pathlib import Path


class FileProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.temp_dir = tempfile.mkdtemp(prefix='safegate_')
        
    def create_zip(self, file_list, output_dir=None):
        if not file_list:
            self.logger.warning("No files to zip")
            return None
            
        if output_dir is None:
            output_dir = self.temp_dir
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"usb_transfer_{timestamp}.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in file_list:
                    if os.path.exists(file_path):
                        arcname = self._get_archive_name(file_path)
                        zipf.write(file_path, arcname)
                        self.logger.debug(f"Added to zip: {file_path} -> {arcname}")
                    else:
                        self.logger.warning(f"File not found, skipping: {file_path}")
                        
            file_size = os.path.getsize(zip_path)
            self.logger.info(f"Created zip file: {zip_path} ({file_size} bytes)")
            
            return zip_path
            
        except Exception as e:
            self.logger.error(f"Error creating zip file: {str(e)}")
            return None
            
    def _get_archive_name(self, file_path):
        file_path = Path(file_path)
        
        if '/media/' in str(file_path) or '/mnt/' in str(file_path):
            parts = file_path.parts
            
            for i, part in enumerate(parts):
                if part in ['media', 'mnt']:
                    if i + 2 < len(parts):
                        return str(Path(*parts[i+2:]))
                    else:
                        return file_path.name
                        
        return str(file_path.relative_to(file_path.anchor))
        
    def get_file_info(self, file_path):
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'extension': Path(file_path).suffix.lower(),
                'name': os.path.basename(file_path)
            }
        except Exception as e:
            self.logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return None
            
    def filter_files_by_type(self, file_list, allowed_extensions=None, blocked_extensions=None):
        if allowed_extensions is None:
            allowed_extensions = []
            
        if blocked_extensions is None:
            blocked_extensions = ['.exe', '.scr', '.bat', '.cmd', '.com', '.pif', '.vbs', '.js']
            
        filtered_files = []
        
        for file_path in file_list:
            file_ext = Path(file_path).suffix.lower()
            
            if blocked_extensions and file_ext in blocked_extensions:
                self.logger.warning(f"Blocked file type: {file_path}")
                continue
                
            if allowed_extensions and file_ext not in allowed_extensions:
                self.logger.warning(f"File type not allowed: {file_path}")
                continue
                
            filtered_files.append(file_path)
            
        return filtered_files
        
    def get_directory_size(self, directory_path):
        total_size = 0
        file_count = 0
        
        try:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        file_count += 1
                    except (OSError, IOError):
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error calculating directory size: {str(e)}")
            
        return {'total_size': total_size, 'file_count': file_count}
        
    def create_file_manifest(self, file_list, manifest_path=None):
        if manifest_path is None:
            manifest_path = os.path.join(self.temp_dir, 'file_manifest.txt')
            
        try:
            with open(manifest_path, 'w') as f:
                f.write(f"USB Transfer Manifest\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Files: {len(file_list)}\n")
                f.write("-" * 50 + "\n\n")
                
                for file_path in file_list:
                    file_info = self.get_file_info(file_path)
                    if file_info:
                        f.write(f"File: {file_info['name']}\n")
                        f.write(f"Path: {file_path}\n")
                        f.write(f"Size: {file_info['size']} bytes\n")
                        f.write(f"Modified: {file_info['modified']}\n")
                        f.write(f"Extension: {file_info['extension']}\n")
                        f.write("-" * 30 + "\n")
                        
            self.logger.info(f"File manifest created: {manifest_path}")
            return manifest_path
            
        except Exception as e:
            self.logger.error(f"Error creating file manifest: {str(e)}")
            return None
            
    def cleanup_temp_files(self):
        try:
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            self.logger.error(f"Error cleaning up temp files: {str(e)}")
            
    def verify_zip_integrity(self, zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                bad_files = zipf.testzip()
                if bad_files:
                    self.logger.error(f"Zip integrity check failed: {bad_files}")
                    return False
                else:
                    self.logger.info(f"Zip integrity check passed: {zip_path}")
                    return True
                    
        except Exception as e:
            self.logger.error(f"Error verifying zip integrity: {str(e)}")
            return False
            
    def __del__(self):
        self.cleanup_temp_files()