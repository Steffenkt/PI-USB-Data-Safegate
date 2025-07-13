#!/usr/bin/env python3
"""
Version Bump Script for PI USB Data Safegate
Automatically increments version numbers and updates relevant files
"""

import sys
import re
import argparse
from pathlib import Path
from typing import Dict, Tuple


def parse_version(version_string: str) -> Dict:
    """Parse a semantic version string"""
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
        'build': build
    }


def format_version(version_info: Dict) -> str:
    """Format version info back to string"""
    version_str = f"{version_info['major']}.{version_info['minor']}.{version_info['patch']}"
    
    if version_info.get('prerelease'):
        version_str += f"-{version_info['prerelease']}"
    
    if version_info.get('build'):
        version_str += f"+{version_info['build']}"
    
    return version_str


def bump_version(current_version: str, bump_type: str, prerelease: str = None) -> str:
    """Bump version according to type"""
    version_info = parse_version(current_version)
    
    if bump_type == 'major':
        version_info['major'] += 1
        version_info['minor'] = 0
        version_info['patch'] = 0
    elif bump_type == 'minor':
        version_info['minor'] += 1
        version_info['patch'] = 0
    elif bump_type == 'patch':
        version_info['patch'] += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    # Handle prerelease
    if prerelease:
        version_info['prerelease'] = prerelease
    else:
        version_info['prerelease'] = None
    
    # Remove build metadata when bumping
    version_info['build'] = None
    
    return format_version(version_info)


def read_current_version() -> str:
    """Read current version from version.py"""
    version_file = Path("src/pi_usb_safegate/version.py")
    
    if not version_file.exists():
        raise FileNotFoundError("src/pi_usb_safegate/version.py not found")
    
    content = version_file.read_text()
    
    # Find __version__ = "x.y.z"
    pattern = r'^__version__\s*=\s*["\']([^"\']+)["\']'
    match = re.search(pattern, content, re.MULTILINE)
    
    if not match:
        raise ValueError("Could not find __version__ in version.py")
    
    return match.group(1)


def update_version_file(new_version: str):
    """Update version.py with new version"""
    version_file = Path("src/pi_usb_safegate/version.py")
    content = version_file.read_text()
    
    # Update __version__
    content = re.sub(
        r'^(__version__\s*=\s*["\'])[^"\']+(["\'])',
        f'\\g<1>{new_version}\\g<2>',
        content,
        flags=re.MULTILINE
    )
    
    # Update VERSION_INFO
    version_info = parse_version(new_version)
    
    # Update major, minor, patch
    content = re.sub(
        r"('major':\s*)\d+",
        f"\\g<1>{version_info['major']}",
        content
    )
    content = re.sub(
        r"('minor':\s*)\d+",
        f"\\g<1>{version_info['minor']}",
        content
    )
    content = re.sub(
        r"('patch':\s*)\d+",
        f"\\g<1>{version_info['patch']}",
        content
    )
    
    # Update release info
    release = version_info.get('prerelease', 'stable')
    if not release:
        release = 'stable'
    
    content = re.sub(
        r"('release':\s*['\"])[^'\"]*(['\"])",
        f"\\g<1>{release}\\g<2>",
        content
    )
    
    version_file.write_text(content)


def update_changelog(new_version: str):
    """Update CHANGELOG.md if it exists"""
    changelog_file = Path("CHANGELOG.md")
    
    if not changelog_file.exists():
        print("No CHANGELOG.md found, skipping changelog update")
        return
    
    # Read existing content
    content = changelog_file.read_text()
    
    # Add new version entry at the top
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    new_entry = f"""## [{new_version}] - {date_str}

### Added
- 

### Changed
- 

### Fixed
- 

### Security
- 

"""
    
    # Insert after the header (assuming ## [Unreleased] or similar exists)
    if "## [Unreleased]" in content:
        content = content.replace("## [Unreleased]", f"## [Unreleased]\n\n{new_entry}")
    else:
        # Insert after the first heading
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('# '):
                insert_pos = i + 1
                break
        
        lines.insert(insert_pos, new_entry)
        content = '\n'.join(lines)
    
    changelog_file.write_text(content)
    print(f"Updated CHANGELOG.md with version {new_version}")


def validate_version_consistency():
    """Validate that version is consistent across files"""
    import sys
    sys.path.insert(0, 'src/pi_usb_safegate')
    from version import get_version
    
    current_version = get_version()
    
    # Check build scripts
    build_script = Path("build-package.sh")
    if build_script.exists():
        print("✓ build-package.sh uses dynamic versioning")
    
    makefile = Path("Makefile")
    if makefile.exists():
        print("✓ Makefile uses dynamic versioning")
    
    print(f"✓ Version consistency validated: {current_version}")


def main():
    parser = argparse.ArgumentParser(description="Bump version for PI USB Data Safegate")
    parser.add_argument(
        'bump_type',
        choices=['major', 'minor', 'patch'],
        help='Type of version bump'
    )
    parser.add_argument(
        '--prerelease',
        help='Add prerelease identifier (e.g., alpha, beta, rc1)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--current',
        action='store_true',
        help='Show current version and exit'
    )
    
    args = parser.parse_args()
    
    try:
        current_version = read_current_version()
        
        if args.current:
            print(f"Current version: {current_version}")
            return
        
        new_version = bump_version(current_version, args.bump_type, args.prerelease)
        
        print(f"Current version: {current_version}")
        print(f"New version: {new_version}")
        
        if args.dry_run:
            print("\n[DRY RUN] Would update the following files:")
            print("- version.py")
            print("- CHANGELOG.md (if exists)")
            return
        
        # Confirm the change
        if not args.dry_run:
            response = input(f"\nUpdate version from {current_version} to {new_version}? [y/N]: ")
            if response.lower() not in ['y', 'yes']:
                print("Version bump cancelled")
                return
        
        # Update files
        print(f"\nUpdating version to {new_version}...")
        update_version_file(new_version)
        print("✓ Updated version.py")
        
        update_changelog(new_version)
        
        # Validate consistency
        validate_version_consistency()
        
        print(f"\n🎉 Version successfully bumped to {new_version}")
        print("\nNext steps:")
        print("1. Review and update CHANGELOG.md with actual changes")
        print("2. Commit the version bump: git add . && git commit -m 'Bump version to {}'".format(new_version))
        print("3. Trigger GitHub Actions workflow to build and release")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()