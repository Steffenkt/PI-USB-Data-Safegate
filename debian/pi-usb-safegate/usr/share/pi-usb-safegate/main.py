#! /usr/bin/python3
"""
PI USB Data Safegate - Main Application
Secure USB to cloud transfer application for Raspberry Pi
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging
from datetime import datetime
import os
import sys

from .version import get_version, get_app_title, get_version_string_long
from .modules.config_manager import ConfigManager
from .modules.usb_detector import USBDetector
from .modules.malware_scanner import MalwareScanner
from .modules.file_processor import FileProcessor
from .modules.cloud_uploader import CloudUploader
from .modules.email_notifier import EmailNotifier
from .modules.cleanup_scheduler import CleanupScheduler


class SafegateApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(get_app_title())
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.config = ConfigManager()
        self.usb_detector = USBDetector()
        self.scanner = MalwareScanner()
        self.file_processor = FileProcessor()
        self.uploader = CloudUploader(self.config)
        self.notifier = EmailNotifier(self.config)
        self.cleanup = CleanupScheduler(self.config)
        
        self.selected_usb = None
        self.user_email = tk.StringVar()
        
        self.setup_logging()
        self.create_gui()
        
        # Update log file path to system location if package installed
        if os.path.exists('/var/log/pi-usb-safegate'):
            self.setup_system_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('safegate.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_system_logging(self):
        """Setup logging for system installation"""
        log_dir = '/var/log/pi-usb-safegate'
        os.makedirs(log_dir, exist_ok=True)
        
        # Create new handler for system log
        log_file = os.path.join(log_dir, 'safegate.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        
        self.logger.info(f"System logging configured: {log_file}")
        
    def create_gui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(main_frame, text=get_app_title(), 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(main_frame, text="Select USB Drive:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.usb_combo = ttk.Combobox(main_frame, state="readonly", width=50)
        self.usb_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        refresh_btn = ttk.Button(main_frame, text="Refresh USB List", 
                                command=self.refresh_usb_list)
        refresh_btn.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Your Email:").grid(row=3, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(main_frame, textvariable=self.user_email, width=50)
        email_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        process_btn = ttk.Button(main_frame, text="Scan and Upload Files", 
                                command=self.start_processing, style='Accent.TButton')
        process_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="Status:").grid(row=6, column=0, sticky=(tk.W, tk.N), pady=5)
        self.status_text = scrolledtext.ScrolledText(main_frame, height=15, width=70)
        self.status_text.grid(row=6, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        
        main_frame.rowconfigure(6, weight=1)
        
        self.refresh_usb_list()
        
    def log_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.status_text.insert(tk.END, formatted_message)
        self.status_text.see(tk.END)
        self.root.update()
        self.logger.info(message)
        
    def refresh_usb_list(self):
        self.log_status("Searching for USB drives...")
        usb_drives = self.usb_detector.get_usb_drives()
        
        if usb_drives:
            drive_list = [f"{drive['device']} - {drive['label']} ({drive['size']})" 
                         for drive in usb_drives]
            self.usb_combo['values'] = drive_list
            self.usb_combo.current(0)
            self.log_status(f"Found {len(usb_drives)} USB drive(s)")
        else:
            self.usb_combo['values'] = []
            self.log_status("No USB drives found")
            
    def start_processing(self):
        if not self.usb_combo.get():
            messagebox.showerror("Error", "Please select a USB drive")
            return
            
        if not self.user_email.get().strip():
            messagebox.showerror("Error", "Please enter your email address")
            return
            
        self.selected_usb = self.usb_detector.get_usb_drives()[self.usb_combo.current()]
        
        thread = threading.Thread(target=self.process_files, daemon=True)
        thread.start()
        
    def process_files(self):
        try:
            self.progress.start()
            
            self.log_status(f"Starting scan of {self.selected_usb['device']}...")
            
            scan_result = self.scanner.scan_usb_drive(self.selected_usb['mountpoint'])
            
            if scan_result['infected_files']:
                self.log_status(f"WARNING: {len(scan_result['infected_files'])} infected files found!")
                for infected_file in scan_result['infected_files']:
                    self.log_status(f"  - {infected_file}")
                self.log_status("Infected files will NOT be uploaded")
            else:
                self.log_status("No threats detected - all files are safe")
                
            if scan_result['safe_files']:
                self.log_status(f"Zipping {len(scan_result['safe_files'])} safe files...")
                zip_path = self.file_processor.create_zip(scan_result['safe_files'])
                
                self.log_status("Uploading to cloud storage...")
                download_link = self.uploader.upload_file(zip_path)
                
                if download_link:
                    self.log_status(f"Upload successful! Download link: {download_link}")
                    
                    self.log_status("Sending email notification...")
                    email_sent = self.notifier.send_notification(
                        self.user_email.get().strip(), download_link, zip_path)
                    
                    if email_sent:
                        self.log_status("Email sent successfully!")
                        
                        self.cleanup.schedule_deletion(zip_path, download_link)
                        self.log_status("File scheduled for deletion in 7 days")
                    else:
                        self.log_status("Failed to send email notification")
                else:
                    self.log_status("Upload failed!")
            else:
                self.log_status("No safe files to upload")
                
        except Exception as e:
            self.log_status(f"Error during processing: {str(e)}")
            self.logger.error(f"Processing error: {str(e)}", exc_info=True)
        finally:
            self.progress.stop()
            
    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("Application terminated by user")
        except Exception as e:
            self.logger.error(f"Application error: {str(e)}", exc_info=True)


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This application requires root privileges to access USB devices.")
        print("Please run with: sudo python3 main.py")
        sys.exit(1)
        
    app = SafegateApp()
    app.run()