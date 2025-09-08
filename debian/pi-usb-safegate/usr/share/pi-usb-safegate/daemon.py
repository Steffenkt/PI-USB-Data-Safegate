#! /usr/bin/python3
"""
Secure Nextcloud USB Uploader Daemon
A headless daemon that monitors USB drives, scans for malware, and uploads to Nextcloud
"""

import os
import sys
import signal
import logging
import time
import threading
import queue
from pathlib import Path
from datetime import datetime

from .version import get_version, get_app_title, get_version_string_long
from .modules.config_manager import ConfigManager
from .modules.usb_monitor import USBMonitor
from .modules.malware_scanner import MalwareScanner
from .modules.file_processor import FileProcessor
from .modules.nextcloud_uploader import NextcloudUploader
from .modules.email_notifier import EmailNotifier
from .modules.cleanup_scheduler import CleanupScheduler
from .modules.status_manager import StatusManager


class USBSafegateService:
    """Main daemon service class"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.logger = self._setup_logging()
        self.running = False
        self.shutdown_event = threading.Event()
        self.processing_queue = queue.Queue()
        
        # Initialize components
        self.usb_monitor = USBMonitor(self.on_usb_inserted, self.on_usb_removed)
        self.scanner = MalwareScanner()
        self.file_processor = FileProcessor()
        self.uploader = NextcloudUploader(self.config)
        self.notifier = EmailNotifier(self.config)
        self.cleanup = CleanupScheduler(self.config)
        self.status = StatusManager()
        
        # Processing thread
        self.processing_thread = None
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get_logging_config()
        
        # Create log directory if it doesn't exist
        log_dir = Path('/var/log/pi-usb-safegate')
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_config['log_level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'daemon.log'),
                logging.StreamHandler() if '--debug' in sys.argv else logging.NullHandler()
            ]
        )
        
        return logging.getLogger(__name__)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        
    def on_usb_inserted(self, device_info):
        """Handle USB device insertion"""
        self.logger.info(f"USB device inserted: {device_info}")
        self.status.set_status("USB device detected", "processing")
        
        # Add to processing queue
        self.processing_queue.put({
            'action': 'process_usb',
            'device': device_info,
            'timestamp': datetime.now()
        })
        
    def on_usb_removed(self, device_info):
        """Handle USB device removal"""
        self.logger.info(f"USB device removed: {device_info}")
        self.status.set_status("USB device removed", "idle")
        
    def _processing_worker(self):
        """Worker thread for processing USB drives"""
        while self.running and not self.shutdown_event.is_set():
            try:
                # Wait for work with timeout
                try:
                    work_item = self.processing_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                    
                if work_item['action'] == 'process_usb':
                    self._process_usb_drive(work_item['device'])
                    
                self.processing_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error in processing worker: {e}", exc_info=True)
                self.status.set_status(f"Processing error: {e}", "error")
                
    def _process_usb_drive(self, device_info):
        """Process a USB drive"""
        try:
            mount_point = device_info.get('mount_point')
            if not mount_point or not os.path.exists(mount_point):
                self.logger.warning(f"Invalid mount point: {mount_point}")
                return
                
            self.logger.info(f"Processing USB drive at {mount_point}")
            self.status.set_status(f"Scanning files in {mount_point}", "scanning")
            
            # Scan for malware
            scan_result = self.scanner.scan_directory(mount_point)
            
            if scan_result['infected_files']:
                self.logger.warning(f"Malware detected in {len(scan_result['infected_files'])} files")
                self.status.set_status(f"Malware detected! {len(scan_result['infected_files'])} infected files", "error")
                
                # Show GUI warning
                self._show_malware_warning(scan_result['infected_files'])
                return
                
            if not scan_result['safe_files']:
                self.logger.info("No files found on USB drive")
                self.status.set_status("No files found on USB drive", "idle")
                return
                
            # Create ZIP archive
            self.status.set_status(f"Creating archive from {len(scan_result['safe_files'])} files", "processing")
            zip_path = self.file_processor.create_zip(scan_result['safe_files'])
            
            if not zip_path:
                self.logger.error("Failed to create ZIP archive")
                self.status.set_status("Failed to create archive", "error")
                return
                
            # Upload to Nextcloud
            self.status.set_status("Uploading to Nextcloud", "uploading")
            upload_result = self.uploader.upload_file(zip_path)
            
            if not upload_result['success']:
                self.logger.error(f"Upload failed: {upload_result['error']}")
                self.status.set_status(f"Upload failed: {upload_result['error']}", "error")
                return
                
            # Generate public share link
            self.status.set_status("Generating public share link", "processing")
            share_link = self.uploader.create_public_share(upload_result['remote_path'])
            
            if not share_link:
                self.logger.error("Failed to create public share link")
                self.status.set_status("Failed to create share link", "error")
                return
                
            # Get email address from GUI
            email_address = self._get_email_address()
            
            if not email_address:
                self.logger.warning("No email address provided")
                self.status.set_status("No email address provided", "warning")
                return
                
            # Send email notification
            self.status.set_status("Sending email notification", "processing")
            email_sent = self.notifier.send_notification(email_address, share_link, zip_path)
            
            if email_sent:
                self.logger.info(f"Email notification sent to {email_address}")
                self.status.set_status(f"Email sent to {email_address}", "success")
                
                # Schedule cleanup
                self.cleanup.schedule_deletion(upload_result['remote_path'], share_link)
                
            else:
                self.logger.error("Failed to send email notification")
                self.status.set_status("Failed to send email", "error")
                
        except Exception as e:
            self.logger.error(f"Error processing USB drive: {e}", exc_info=True)
            self.status.set_status(f"Processing error: {e}", "error")
            
    def _show_malware_warning(self, infected_files):
        """Show GUI warning for malware detection"""
        try:
            # Import GUI components only when needed
            import tkinter as tk
            from tkinter import messagebox
            
            # Create temporary root window
            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            # Create warning message
            message = f"⚠️ MALWARE DETECTED! ⚠️\n\n"
            message += f"Found {len(infected_files)} infected files:\n\n"
            
            for infected_file in infected_files[:5]:  # Show first 5 files
                file_path = infected_file.get('file', 'Unknown')
                threat = infected_file.get('threat', 'Unknown threat')
                message += f"• {os.path.basename(file_path)}: {threat}\n"
                
            if len(infected_files) > 5:
                message += f"... and {len(infected_files) - 5} more files\n"
                
            message += "\n❌ Files will NOT be uploaded for security reasons."
            
            messagebox.showerror("Malware Detected", message)
            root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error showing malware warning: {e}")
            
    def _get_email_address(self):
        """Get email address from user via GUI"""
        try:
            # Import GUI components only when needed
            import tkinter as tk
            from tkinter import simpledialog
            
            # Create temporary root window
            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            # Get email address from user
            email = simpledialog.askstring(
                "Email Address",
                "Enter email address to receive download link:",
                parent=root
            )
            
            root.destroy()
            return email
            
        except Exception as e:
            self.logger.error(f"Error getting email address: {e}")
            return None
            
    def start(self):
        """Start the daemon service"""
        if self.running:
            self.logger.warning("Service is already running")
            return
            
        self.logger.info(f"Starting {get_version_string_long()}")
        self.running = True
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._processing_worker, daemon=True)
        self.processing_thread.start()
        
        # Start USB monitoring
        self.usb_monitor.start()
        
        # Start cleanup scheduler
        self.cleanup.start()
        
        # Test system components
        self._test_system()
        
        self.status.set_status("Service started - monitoring for USB drives", "idle")
        self.logger.info("USB Safegate Service started successfully")
        
    def stop(self):
        """Stop the daemon service"""
        if not self.running:
            return
            
        self.logger.info("Stopping USB Safegate Service")
        self.running = False
        self.shutdown_event.set()
        
        # Stop components
        self.usb_monitor.stop()
        self.cleanup.stop()
        
        # Wait for processing thread to finish
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=10)
            
        self.status.set_status("Service stopped", "stopped")
        self.logger.info("USB Safegate Service stopped")
        
    def _test_system(self):
        """Test system components on startup"""
        try:
            # Test ClamAV
            if not self.scanner.test_connection():
                self.logger.warning("ClamAV test failed")
                
            # Test Nextcloud connection
            if not self.uploader.test_connection():
                self.logger.warning("Nextcloud connection test failed")
                
            # Test email configuration
            if not self.notifier.test_email_connection():
                self.logger.warning("Email configuration test failed")
                
        except Exception as e:
            self.logger.error(f"System test error: {e}")
            
    def run(self):
        """Main run loop"""
        self.start()
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
            
        finally:
            self.stop()


def main():
    """Main entry point"""
    # Check if running as root
    if os.geteuid() != 0:
        print("This service requires root privileges to access USB devices.")
        print("Please run with: sudo python3 daemon.py")
        sys.exit(1)
        
    # Create service instance
    service = USBSafegateService()
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start':
            service.run()
        elif command == 'stop':
            service.stop()
        elif command == 'test':
            service._test_system()
        elif command == 'status':
            print(f"Status: {service.status.get_status()}")
        else:
            print(f"Unknown command: {command}")
            print("Usage: daemon.py [start|stop|test|status]")
            sys.exit(1)
    else:
        # Default: run the service
        service.run()


if __name__ == "__main__":
    main()