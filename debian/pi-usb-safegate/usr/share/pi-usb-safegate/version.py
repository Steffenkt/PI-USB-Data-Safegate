#! /usr/bin/python3
"""
PI USB Data Safegate - Version Management
Centralized version information for the application
"""

import re
from typing import Tuple, Dict


# Application Version (Semantic Versioning)
__version__ = "1.0.1"

# Version metadata
VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'patch': 1,
    'release': 'stable',  # stable, beta, alpha, dev
    'build': None
}

# Application metadata
APP_NAME = "PI USB Data Safegate"
APP_DESCRIPTION = "Secure USB to cloud transfer with malware scanning"
APP_AUTHOR = "Steffen Kaster"
APP_EMAIL = "skaster@kaster-development.de"
APP_URL = "https://github.com/Steffenkt/PI-USB-Data-Safegate"
APP_LICENSE = "MIT"

# Package metadata
PACKAGE_NAME = "pi-usb-safegate"
PACKAGE_ARCHITECTURE = "all"
PACKAGE_SECTION = "utils"
PACKAGE_PRIORITY = "optional"


def get_version() -> str:
    """Get the current version string"""
    return __version__


def get_version_info() -> Dict:
    """Get detailed version information"""
    return VERSION_INFO.copy()


def get_version_tuple() -> Tuple[int, int, int]:
    """Get version as tuple (major, minor, patch)"""
    return (VERSION_INFO['major'], VERSION_INFO['minor'], VERSION_INFO['patch'])


def get_package_filename() -> str:
    """Get the .deb package filename with version"""
    return f"{PACKAGE_NAME}_{__version__}_{PACKAGE_ARCHITECTURE}.deb"


def get_app_title() -> str:
    """Get formatted application title with version"""
    return f"{APP_NAME} v{__version__}"


def get_version_string_long() -> str:
    """Get detailed version string for logs and about dialogs"""
    version_str = f"{APP_NAME} {__version__}"
    
    if VERSION_INFO['release'] != 'stable':
        version_str += f"-{VERSION_INFO['release']}"
    
    if VERSION_INFO['build']:
        version_str += f"+{VERSION_INFO['build']}"
        
    return version_str


def parse_version(version_string: str) -> Dict:
    """Parse a semantic version string into components"""
    # Regex for semantic version: major.minor.patch[-prerelease][+build]
    pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-\.]+))?(?:\+([a-zA-Z0-9\-\.]+))?$'
    
    match = re.match(pattern, version_string)
    if not match:
        raise ValueError(f"Invalid version string: {version_string}")
    
    major, minor, patch, prerelease, build = match.groups()
    
    return {
        'major': int(major),
        'minor': int(minor),
        'patch': int(patch),
        'prerelease': prerelease,
        'build': build,
        'version_string': version_string
    }


def compare_versions(version1: str, version2: str) -> int:
    """Compare two version strings
    
    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    v1 = parse_version(version1)
    v2 = parse_version(version2)
    
    # Compare major.minor.patch
    for component in ['major', 'minor', 'patch']:
        if v1[component] < v2[component]:
            return -1
        elif v1[component] > v2[component]:
            return 1
    
    # If major.minor.patch are equal, compare prerelease
    if v1['prerelease'] and v2['prerelease']:
        if v1['prerelease'] < v2['prerelease']:
            return -1
        elif v1['prerelease'] > v2['prerelease']:
            return 1
    elif v1['prerelease'] and not v2['prerelease']:
        return -1  # prerelease < stable
    elif not v1['prerelease'] and v2['prerelease']:
        return 1   # stable > prerelease
    
    return 0


def is_compatible_version(required_version: str, current_version: str = None) -> bool:
    """Check if current version is compatible with required version"""
    if current_version is None:
        current_version = __version__
    
    try:
        required = parse_version(required_version)
        current = parse_version(current_version)
        
        # Compatible if major version matches and current >= required
        if current['major'] != required['major']:
            return False
            
        if current['minor'] < required['minor']:
            return False
            
        if current['minor'] == required['minor'] and current['patch'] < required['patch']:
            return False
            
        return True
        
    except ValueError:
        return False


def get_build_info() -> Dict:
    """Get build information for debugging"""
    import sys
    import platform
    from datetime import datetime
    
    return {
        'version': __version__,
        'python_version': sys.version,
        'platform': platform.platform(),
        'architecture': platform.machine(),
        'build_time': datetime.now().isoformat(),
        'app_name': APP_NAME,
        'package_name': PACKAGE_NAME
    }


def print_version_info():
    """Print detailed version information (for CLI usage)"""
    print(f"{APP_NAME} {__version__}")
    print(f"Package: {PACKAGE_NAME}")
    print(f"Architecture: {PACKAGE_ARCHITECTURE}")
    print(f"Release: {VERSION_INFO['release']}")
    
    if VERSION_INFO['build']:
        print(f"Build: {VERSION_INFO['build']}")
    
    print(f"Author: {APP_AUTHOR}")
    print(f"License: {APP_LICENSE}")
    print(f"URL: {APP_URL}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "version":
            print(__version__)
        elif command == "info":
            print_version_info()
        elif command == "package":
            print(get_package_filename())
        elif command == "build-info":
            import json
            print(json.dumps(get_build_info(), indent=2))
        else:
            print(f"Unknown command: {command}")
            print("Usage: python version.py [version|info|package|build-info]")
            sys.exit(1)
    else:
        print_version_info()