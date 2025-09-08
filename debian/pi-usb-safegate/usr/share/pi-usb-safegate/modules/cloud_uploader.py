"""
Cloud Storage Upload Module
Handles uploading files to various cloud storage providers
"""

import os
import requests
import logging
from urllib.parse import urljoin
import base64
import json


class CloudUploader:
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.cloud_config = self.config.get_cloud_config()
        
    def upload_file(self, file_path):
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return None
            
        provider = self.cloud_config['provider']
        
        if provider == 'nextcloud':
            return self._upload_to_nextcloud(file_path)
        elif provider == 'dropbox':
            return self._upload_to_dropbox(file_path)
        else:
            self.logger.error(f"Unsupported cloud provider: {provider}")
            return None
            
    def _upload_to_nextcloud(self, file_path):
        try:
            filename = os.path.basename(file_path)
            
            upload_url = urljoin(self.cloud_config['url'], 
                               f"/remote.php/dav/files/{self.cloud_config['username']}"
                               f"{self.cloud_config['upload_path']}/{filename}")
            
            auth = (self.cloud_config['username'], self.cloud_config['password'])
            
            self.logger.info(f"Uploading to Nextcloud: {filename}")
            
            with open(file_path, 'rb') as f:
                response = requests.put(upload_url, data=f, auth=auth, timeout=300)
                
            if response.status_code in [200, 201, 204]:
                self.logger.info(f"Upload successful: {filename}")
                
                share_link = self._create_nextcloud_share(filename)
                return share_link
            else:
                self.logger.error(f"Upload failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error during upload: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error uploading to Nextcloud: {str(e)}")
            return None
            
    def _create_nextcloud_share(self, filename):
        try:
            share_url = urljoin(self.cloud_config['url'], "/ocs/v2.php/apps/files_sharing/api/v1/shares")
            
            auth = (self.cloud_config['username'], self.cloud_config['password'])
            
            data = {
                'path': f"{self.cloud_config['upload_path']}/{filename}",
                'shareType': 3,  # Public link
                'permissions': 1,  # Read only
                'expireDate': None
            }
            
            headers = {
                'OCS-APIRequest': 'true',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(share_url, data=data, auth=auth, headers=headers, timeout=30)
            
            if response.status_code == 200:
                if response.headers.get('content-type', '').startswith('application/json'):
                    share_data = response.json()
                else:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.text)
                    url_element = root.find('.//url')
                    if url_element is not None:
                        return url_element.text
                        
                if 'ocs' in share_data and 'data' in share_data['ocs']:
                    return share_data['ocs']['data']['url']
                    
            self.logger.error(f"Failed to create share link: {response.status_code}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating Nextcloud share: {str(e)}")
            return None
            
    def _upload_to_dropbox(self, file_path):
        try:
            filename = os.path.basename(file_path)
            
            url = "https://content.dropboxapi.com/2/files/upload"
            
            headers = {
                'Authorization': f'Bearer {self.cloud_config["access_token"]}',
                'Dropbox-API-Arg': json.dumps({
                    'path': f'/{filename}',
                    'mode': 'add',
                    'autorename': True
                }),
                'Content-Type': 'application/octet-stream'
            }
            
            self.logger.info(f"Uploading to Dropbox: {filename}")
            
            with open(file_path, 'rb') as f:
                response = requests.post(url, data=f, headers=headers, timeout=300)
                
            if response.status_code == 200:
                self.logger.info(f"Upload successful: {filename}")
                upload_data = response.json()
                
                share_link = self._create_dropbox_share(upload_data['path_display'])
                return share_link
            else:
                self.logger.error(f"Upload failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error uploading to Dropbox: {str(e)}")
            return None
            
    def _create_dropbox_share(self, file_path):
        try:
            url = "https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings"
            
            headers = {
                'Authorization': f'Bearer {self.cloud_config["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'path': file_path,
                'settings': {
                    'requested_visibility': 'public',
                    'audience': 'public',
                    'access': 'viewer'
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                share_data = response.json()
                return share_data['url']
            else:
                self.logger.error(f"Failed to create Dropbox share: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating Dropbox share: {str(e)}")
            return None
            
    def delete_file(self, file_identifier):
        provider = self.cloud_config['provider']
        
        if provider == 'nextcloud':
            return self._delete_from_nextcloud(file_identifier)
        elif provider == 'dropbox':
            return self._delete_from_dropbox(file_identifier)
        else:
            self.logger.error(f"Unsupported cloud provider: {provider}")
            return False
            
    def _delete_from_nextcloud(self, filename):
        try:
            delete_url = urljoin(self.cloud_config['url'], 
                               f"/remote.php/dav/files/{self.cloud_config['username']}"
                               f"{self.cloud_config['upload_path']}/{filename}")
            
            auth = (self.cloud_config['username'], self.cloud_config['password'])
            
            response = requests.delete(delete_url, auth=auth, timeout=30)
            
            if response.status_code in [200, 204]:
                self.logger.info(f"File deleted from Nextcloud: {filename}")
                return True
            else:
                self.logger.error(f"Failed to delete file: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting from Nextcloud: {str(e)}")
            return False
            
    def _delete_from_dropbox(self, file_path):
        try:
            url = "https://api.dropboxapi.com/2/files/delete_v2"
            
            headers = {
                'Authorization': f'Bearer {self.cloud_config["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            data = {'path': file_path}
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                self.logger.info(f"File deleted from Dropbox: {file_path}")
                return True
            else:
                self.logger.error(f"Failed to delete file: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting from Dropbox: {str(e)}")
            return False
            
    def test_connection(self):
        provider = self.cloud_config['provider']
        
        if provider == 'nextcloud':
            return self._test_nextcloud_connection()
        elif provider == 'dropbox':
            return self._test_dropbox_connection()
        else:
            return False
            
    def _test_nextcloud_connection(self):
        try:
            test_url = urljoin(self.cloud_config['url'], "/status.php")
            auth = (self.cloud_config['username'], self.cloud_config['password'])
            
            response = requests.get(test_url, auth=auth, timeout=10)
            
            if response.status_code == 200:
                self.logger.info("Nextcloud connection test successful")
                return True
            else:
                self.logger.error(f"Nextcloud connection test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Nextcloud connection test error: {str(e)}")
            return False
            
    def _test_dropbox_connection(self):
        try:
            url = "https://api.dropboxapi.com/2/users/get_current_account"
            
            headers = {
                'Authorization': f'Bearer {self.cloud_config["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.logger.info("Dropbox connection test successful")
                return True
            else:
                self.logger.error(f"Dropbox connection test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Dropbox connection test error: {str(e)}")
            return False