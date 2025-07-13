#!/usr/bin/env python3
"""
PI USB Data Safegate - Secure USB to cloud transfer with malware scanning

A headless Raspberry Pi application that monitors USB devices, scans for malware,
and securely uploads files to Nextcloud with email notifications.
"""

from .version import __version__, get_version, get_app_title

__all__ = ['__version__', 'get_version', 'get_app_title']