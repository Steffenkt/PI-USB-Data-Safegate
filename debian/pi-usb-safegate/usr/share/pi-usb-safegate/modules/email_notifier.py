"""
Email Notification Module
Handles sending email notifications with download links
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime


class EmailNotifier:
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.email_config = self.config.get_email_config()
        
    def send_notification(self, recipient_email, download_link, zip_file_path):
        try:
            msg = self._create_email_message(recipient_email, download_link, zip_file_path)
            
            self.logger.info(f"Sending email notification to {recipient_email}")
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['smtp_username'], self.email_config['smtp_password'])
                
                text = msg.as_string()
                server.sendmail(self.email_config['smtp_username'], recipient_email, text)
                
            self.logger.info(f"Email sent successfully to {recipient_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP authentication failed: {str(e)}")
            return False
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
            
    def _create_email_message(self, recipient_email, download_link, zip_file_path):
        msg = MIMEMultipart()
        
        msg['From'] = f"{self.email_config['sender_name']} <{self.email_config['smtp_username']}>"
        msg['To'] = recipient_email
        msg['Subject'] = "USB Data Transfer Complete - Download Link"
        
        body = self._create_email_body(download_link, zip_file_path)
        msg.attach(MIMEText(body, 'html'))
        
        return msg
        
    def _create_email_body(self, download_link, zip_file_path):
        file_name = os.path.basename(zip_file_path)
        file_size = self._format_file_size(os.path.getsize(zip_file_path))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 0 0 8px 8px;
                }}
                .download-button {{
                    display: inline-block;
                    background-color: #008CBA;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                .download-button:hover {{
                    background-color: #007BB5;
                }}
                .info-box {{
                    background-color: #e7f3ff;
                    border-left: 4px solid #2196F3;
                    padding: 12px;
                    margin: 15px 0;
                }}
                .warning-box {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 12px;
                    margin: 15px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔒 USB Data Transfer Complete</h1>
                <p>Your files have been securely processed and uploaded</p>
            </div>
            
            <div class="content">
                <h2>Transfer Summary</h2>
                
                <div class="info-box">
                    <strong>📁 File:</strong> {file_name}<br>
                    <strong>📊 Size:</strong> {file_size}<br>
                    <strong>🕐 Processed:</strong> {timestamp}
                </div>
                
                <h3>Download Your Files</h3>
                <p>Your USB files have been scanned for malware and are ready for download:</p>
                
                <div style="text-align: center;">
                    <a href="{download_link}" class="download-button">
                        📥 Download Files
                    </a>
                </div>
                
                <div class="warning-box">
                    <strong>⚠️ Important Security Information:</strong><br>
                    • All files were scanned for malware before upload<br>
                    • Only safe files are included in the download<br>
                    • This link will expire in 7 days for security<br>
                    • Please download your files promptly
                </div>
                
                <h3>Security Report</h3>
                <p>✅ All files passed malware scanning<br>
                ✅ Files compressed and encrypted for secure transfer<br>
                ✅ Temporary files removed from processing system</p>
                
                <h3>Need Help?</h3>
                <p>If you experience any issues downloading your files, please contact your system administrator.</p>
            </div>
            
            <div class="footer">
                <p>This email was generated automatically by PI USB Data Safegate<br>
                Please do not reply to this email address</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
        
    def _format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
            
        return f"{size_bytes:.1f} {size_names[i]}"
        
    def send_error_notification(self, recipient_email, error_message):
        try:
            msg = MIMEMultipart()
            
            msg['From'] = f"{self.email_config['sender_name']} <{self.email_config['smtp_username']}>"
            msg['To'] = recipient_email
            msg['Subject'] = "USB Data Transfer - Error Notification"
            
            body = self._create_error_email_body(error_message)
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['smtp_username'], self.email_config['smtp_password'])
                
                text = msg.as_string()
                server.sendmail(self.email_config['smtp_username'], recipient_email, text)
                
            self.logger.info(f"Error notification sent to {recipient_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending error notification: {str(e)}")
            return False
            
    def _create_error_email_body(self, error_message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #f44336;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 0 0 8px 8px;
                }}
                .error-box {{
                    background-color: #ffebee;
                    border-left: 4px solid #f44336;
                    padding: 12px;
                    margin: 15px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚠️ USB Data Transfer Error</h1>
                <p>An error occurred during processing</p>
            </div>
            
            <div class="content">
                <h2>Error Details</h2>
                
                <div class="error-box">
                    <strong>🕐 Time:</strong> {timestamp}<br>
                    <strong>❌ Error:</strong> {error_message}
                </div>
                
                <h3>What to do next:</h3>
                <ul>
                    <li>Check that your USB drive is properly connected</li>
                    <li>Ensure the USB drive is not write-protected</li>
                    <li>Try the transfer process again</li>
                    <li>Contact your system administrator if the problem persists</li>
                </ul>
                
                <h3>Common Solutions:</h3>
                <ul>
                    <li>Remove and reinsert the USB drive</li>
                    <li>Try a different USB port</li>
                    <li>Check your internet connection</li>
                    <li>Ensure the system has sufficient storage space</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>This email was generated automatically by PI USB Data Safegate<br>
                Please do not reply to this email address</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
        
    def test_email_connection(self):
        try:
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['smtp_username'], self.email_config['smtp_password'])
                
            self.logger.info("Email connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Email connection test failed: {str(e)}")
            return False