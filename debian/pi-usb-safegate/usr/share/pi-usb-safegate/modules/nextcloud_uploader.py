"""
Nextcloud Uploader Module
Handles file uploads to Nextcloud using WebDAV API and creates public share links
"""

import os
import logging
import requests
import json
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, quote
from typing import Dict, Optional
from datetime import datetime, timedelta


class NextcloudUploader:
    """Nextcloud file uploader with WebDAV and OCS API support"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.cloud_config = self.config.get_cloud_config()
        
        # Validate configuration
        if self.cloud_config['provider'] != 'nextcloud':
            raise ValueError("NextcloudUploader requires 'nextcloud' provider in config")
            
        self.base_url = self.cloud_config['url'].rstrip('/')
        self.username = self.cloud_config['username']
        self.password = self.cloud_config['password']
        self.upload_path = self.cloud_config['upload_path'].strip('/')
        
        # WebDAV and OCS API endpoints
        self.webdav_url = f"{self.base_url}/remote.php/dav/files/{self.username}"
        self.ocs_url = f"{self.base_url}/ocs/v2.php/apps/files_sharing/api/v1/shares"
        
        # Setup session with authentication
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.headers.update({
            'User-Agent': 'PI-USB-Safegate/1.0',
            'Accept': 'application/json'
        })
        
    def upload_file(self, local_file_path: str, remote_filename: str = None) -> Dict:
        """Upload a file to Nextcloud using WebDAV API"""
        try:
            if not os.path.exists(local_file_path):
                return {'success': False, 'error': f'Local file not found: {local_file_path}'}
                
            # Generate remote filename if not provided
            if remote_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = os.path.basename(local_file_path)
                name, ext = os.path.splitext(base_name)
                remote_filename = f"{name}_{timestamp}{ext}"
                
            # Construct remote path
            remote_path = f"{self.upload_path}/{remote_filename}"
            upload_url = f"{self.webdav_url}/{quote(remote_path)}"
            
            self.logger.info(f"Uploading {local_file_path} to {remote_path}")
            
            # Create upload directory if it doesn't exist
            self._ensure_directory_exists(self.upload_path)
            
            # Upload file
            with open(local_file_path, 'rb') as f:
                response = self.session.put(
                    upload_url,
                    data=f,
                    headers={'Content-Type': 'application/octet-stream'},
                    timeout=300  # 5 minute timeout for large files
                )
                
            if response.status_code in [200, 201, 204]:
                self.logger.info(f"File uploaded successfully: {remote_path}")
                return {
                    'success': True,
                    'remote_path': remote_path,
                    'remote_filename': remote_filename,
                    'upload_url': upload_url
                }
            else:
                error_msg = f"Upload failed: HTTP {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {'success': False, 'error': error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during upload: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Unexpected error during upload: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
    def _ensure_directory_exists(self, directory_path: str):
        """Ensure a directory exists in Nextcloud"""
        try:
            # Check if directory exists
            dir_url = f"{self.webdav_url}/{quote(directory_path)}"
            response = self.session.request('PROPFIND', dir_url, timeout=30)
            
            if response.status_code == 404:
                # Directory doesn't exist, create it
                self.logger.info(f"Creating directory: {directory_path}")
                response = self.session.request('MKCOL', dir_url, timeout=30)
                
                if response.status_code not in [200, 201]:
                    raise Exception(f"Failed to create directory: HTTP {response.status_code}")
                    
        except Exception as e:
            self.logger.error(f"Error ensuring directory exists: {e}")
            # Continue anyway, upload might still work
            
    def create_public_share(self, remote_path: str, password: str = None, 
                           expire_days: int = None) -> Optional[str]:
        """Create a public share link for a file"""
        try:
            self.logger.info(f"Creating public share for: {remote_path}")
            
            # Prepare share data
            share_data = {
                'path': f"/{remote_path}",
                'shareType': 3,  # Public link
                'permissions': 1,  # Read only
            }
            
            if password:
                share_data['password'] = password
                
            if expire_days:
                expire_date = datetime.now() + timedelta(days=expire_days)
                share_data['expireDate'] = expire_date.strftime('%Y-%m-%d')
                
            # Create share using OCS API
            response = self.session.post(
                self.ocs_url,
                data=share_data,
                headers={
                    'OCS-APIRequest': 'true',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return self._parse_share_response(response)
            else:
                self.logger.error(f"Failed to create share: HTTP {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating public share: {e}")
            return None
            
    def _parse_share_response(self, response: requests.Response) -> Optional[str]:
        """Parse the share creation response to extract the public URL"""
        try:
            # Try JSON first
            content_type = response.headers.get('content-type', '').lower()
            
            if 'json' in content_type:
                data = response.json()
                if 'ocs' in data and 'data' in data['ocs']:
                    return data['ocs']['data'].get('url')
            else:
                # Try XML parsing
                root = ET.fromstring(response.text)
                
                # Look for URL in XML structure
                url_element = root.find('.//url')
                if url_element is not None:
                    return url_element.text
                    
                # Alternative XML structure
                data_element = root.find('.//data')
                if data_element is not None:
                    url_element = data_element.find('url')
                    if url_element is not None:
                        return url_element.text
                        
        except Exception as e:
            self.logger.error(f"Error parsing share response: {e}")
            
        return None
        
    def delete_file(self, remote_path: str) -> bool:
        """Delete a file from Nextcloud"""
        try:
            delete_url = f"{self.webdav_url}/{quote(remote_path)}"
            
            self.logger.info(f"Deleting file: {remote_path}")
            
            response = self.session.delete(delete_url, timeout=30)
            
            if response.status_code in [200, 204]:
                self.logger.info(f"File deleted successfully: {remote_path}")
                return True
            else:
                self.logger.error(f"Failed to delete file: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting file: {e}")
            return False
            
    def list_files(self, directory_path: str = None) -> list:
        """List files in a directory"""
        try:
            if directory_path is None:
                directory_path = self.upload_path
                
            list_url = f"{self.webdav_url}/{quote(directory_path)}"
            
            response = self.session.request(
                'PROPFIND',
                list_url,
                headers={'Depth': '1'},
                timeout=30
            )
            
            if response.status_code == 207:  # Multi-Status
                return self._parse_propfind_response(response.text)
            else:
                self.logger.error(f"Failed to list files: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error listing files: {e}")
            return []
            
    def _parse_propfind_response(self, xml_text: str) -> list:
        """Parse PROPFIND response to extract file information"""
        try:
            root = ET.fromstring(xml_text)
            files = []
            
            for response in root.findall('.//{DAV:}response'):
                href = response.find('.//{DAV:}href')
                if href is not None:
                    file_path = href.text
                    
                    # Extract filename from path
                    if file_path.endswith('/'):
                        continue  # Skip directories
                        
                    filename = os.path.basename(file_path)
                    if filename:
                        files.append({
                            'name': filename,
                            'path': file_path,
                            'href': href.text
                        })
                        
            return files
            
        except Exception as e:
            self.logger.error(f"Error parsing PROPFIND response: {e}")
            return []
            
    def get_file_info(self, remote_path: str) -> Optional[Dict]:
        """Get information about a file"""
        try:
            file_url = f"{self.webdav_url}/{quote(remote_path)}"
            
            response = self.session.request(
                'PROPFIND',
                file_url,
                headers={'Depth': '0'},
                timeout=30
            )
            
            if response.status_code == 207:
                # Parse the XML response to extract file properties
                root = ET.fromstring(response.text)
                
                # Extract basic file information
                info = {
                    'path': remote_path,
                    'exists': True
                }
                
                # Look for size and modification time
                for prop in root.findall('.//{DAV:}prop'):
                    size_elem = prop.find('.//{DAV:}getcontentlength')
                    if size_elem is not None:
                        info['size'] = int(size_elem.text)
                        
                    modified_elem = prop.find('.//{DAV:}getlastmodified')
                    if modified_elem is not None:
                        info['modified'] = modified_elem.text
                        
                return info
                
            elif response.status_code == 404:
                return {'path': remote_path, 'exists': False}
            else:
                self.logger.error(f"Failed to get file info: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return None
            
    def test_connection(self) -> bool:
        """Test connection to Nextcloud"""
        try:
            # Try to access the WebDAV endpoint
            response = self.session.request(
                'PROPFIND',
                self.webdav_url,
                headers={'Depth': '0'},
                timeout=10
            )
            
            if response.status_code in [200, 207]:
                self.logger.info("Nextcloud connection test successful")
                return True
            else:
                self.logger.error(f"Nextcloud connection test failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Nextcloud connection test error: {e}")
            return False
            
    def get_quota_info(self) -> Optional[Dict]:
        """Get storage quota information"""
        try:
            response = self.session.request(
                'PROPFIND',
                self.webdav_url,
                headers={'Depth': '0'},
                data='<?xml version="1.0"?><d:propfind xmlns:d="DAV:"><d:prop><d:quota-available-bytes/><d:quota-used-bytes/></d:prop></d:propfind>',
                timeout=30
            )
            
            if response.status_code == 207:
                root = ET.fromstring(response.text)
                
                quota_info = {}
                for prop in root.findall('.//{DAV:}prop'):
                    available = prop.find('.//{DAV:}quota-available-bytes')
                    used = prop.find('.//{DAV:}quota-used-bytes')
                    
                    if available is not None:
                        quota_info['available'] = int(available.text)
                    if used is not None:
                        quota_info['used'] = int(used.text)
                        
                return quota_info
                
        except Exception as e:
            self.logger.error(f"Error getting quota info: {e}")
            
        return None