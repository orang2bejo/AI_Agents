"""Windows Package Manager (winget) integration for safe application management.

This module provides secure winget operations with proper validation and logging.
"""

import subprocess
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PackageInfo:
    """Information about a winget package."""
    id: str
    name: str
    version: str
    source: str
    available_version: Optional[str] = None
    

class WingetManager:
    """Safe winget operations with validation and logging."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._validate_winget_available()
        
    def _validate_winget_available(self) -> bool:
        """Check if winget is available on the system."""
        try:
            result = subprocess.run(
                ["winget", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info(f"Winget available: {result.stdout.strip()}")
                return True
            else:
                raise RuntimeError("Winget not available")
        except (subprocess.TimeoutExpired, FileNotFoundError, RuntimeError) as e:
            self.logger.error(f"Winget validation failed: {e}")
            raise RuntimeError("Winget is not available on this system")
    
    def search_package(self, query: str, exact: bool = False) -> List[PackageInfo]:
        """Search for packages using winget.
        
        Args:
            query: Search term
            exact: Whether to search for exact match
            
        Returns:
            List of PackageInfo objects
        """
        try:
            cmd = ["winget", "search", query, "--accept-source-agreements"]
            if exact:
                cmd.append("--exact")
                
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"Search failed: {result.stderr}")
                return []
                
            packages = self._parse_search_output(result.stdout)
            self.logger.info(f"Found {len(packages)} packages for query: {query}")
            return packages
            
        except subprocess.TimeoutExpired:
            self.logger.error("Search timeout")
            return []
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return []
    
    def _parse_search_output(self, output: str) -> List[PackageInfo]:
        """Parse winget search output into PackageInfo objects."""
        packages = []
        lines = output.strip().split('\n')
        
        # Skip header lines
        data_start = False
        for line in lines:
            if '---' in line:
                data_start = True
                continue
            if not data_start or not line.strip():
                continue
                
            # Parse package line (Name, Id, Version, Source)
            parts = line.split()
            if len(parts) >= 4:
                # Handle cases where name has spaces
                name_parts = []
                id_found = False
                for i, part in enumerate(parts):
                    if '.' in part and not id_found:  # Likely package ID
                        package_id = part
                        version = parts[i + 1] if i + 1 < len(parts) else "Unknown"
                        source = parts[i + 2] if i + 2 < len(parts) else "Unknown"
                        name = ' '.join(name_parts) if name_parts else parts[0]
                        id_found = True
                        break
                    else:
                        name_parts.append(part)
                        
                if id_found:
                    packages.append(PackageInfo(
                        id=package_id,
                        name=name,
                        version=version,
                        source=source
                    ))
                    
        return packages
    
    def install_package(self, package_id: str, silent: bool = True, 
                       accept_agreements: bool = True) -> Tuple[bool, str]:
        """Install a package using winget.
        
        Args:
            package_id: Package identifier
            silent: Install silently
            accept_agreements: Accept source and package agreements
            
        Returns:
            Tuple of (success, message)
        """
        try:
            cmd = ["winget", "install", package_id]
            
            if silent:
                cmd.append("--silent")
            if accept_agreements:
                cmd.extend(["--accept-source-agreements", "--accept-package-agreements"])
                
            self.logger.info(f"Installing package: {package_id}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                message = f"Successfully installed {package_id}"
                self.logger.info(message)
                return True, message
            else:
                error_msg = f"Installation failed: {result.stderr}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"Installation timeout for {package_id}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Installation error: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def uninstall_package(self, package_id: str, silent: bool = True) -> Tuple[bool, str]:
        """Uninstall a package using winget.
        
        Args:
            package_id: Package identifier
            silent: Uninstall silently
            
        Returns:
            Tuple of (success, message)
        """
        try:
            cmd = ["winget", "uninstall", package_id]
            
            if silent:
                cmd.append("--silent")
                
            self.logger.info(f"Uninstalling package: {package_id}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                message = f"Successfully uninstalled {package_id}"
                self.logger.info(message)
                return True, message
            else:
                error_msg = f"Uninstallation failed: {result.stderr}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"Uninstallation timeout for {package_id}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Uninstallation error: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def list_installed(self) -> List[PackageInfo]:
        """List installed packages.
        
        Returns:
            List of installed PackageInfo objects
        """
        try:
            result = subprocess.run(
                ["winget", "list", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                packages = self._parse_list_output(result.stdout)
                self.logger.info(f"Found {len(packages)} installed packages")
                return packages
            else:
                self.logger.error(f"List failed: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            self.logger.error("List timeout")
            return []
        except Exception as e:
            self.logger.error(f"List error: {e}")
            return []
    
    def _parse_list_output(self, output: str) -> List[PackageInfo]:
        """Parse winget list output into PackageInfo objects."""
        packages = []
        lines = output.strip().split('\n')
        
        # Skip header lines
        data_start = False
        for line in lines:
            if '---' in line:
                data_start = True
                continue
            if not data_start or not line.strip():
                continue
                
            # Parse package line
            parts = line.split()
            if len(parts) >= 3:
                # Handle cases where name has spaces
                name_parts = []
                id_found = False
                for i, part in enumerate(parts):
                    if '.' in part and not id_found:  # Likely package ID
                        package_id = part
                        version = parts[i + 1] if i + 1 < len(parts) else "Unknown"
                        available = parts[i + 2] if i + 2 < len(parts) else None
                        name = ' '.join(name_parts) if name_parts else parts[0]
                        id_found = True
                        break
                    else:
                        name_parts.append(part)
                        
                if id_found:
                    packages.append(PackageInfo(
                        id=package_id,
                        name=name,
                        version=version,
                        source="winget",
                        available_version=available if available != version else None
                    ))
                    
        return packages
    
    def upgrade_package(self, package_id: str, silent: bool = True) -> Tuple[bool, str]:
        """Upgrade a package using winget.
        
        Args:
            package_id: Package identifier
            silent: Upgrade silently
            
        Returns:
            Tuple of (success, message)
        """
        try:
            cmd = ["winget", "upgrade", package_id]
            
            if silent:
                cmd.append("--silent")
            cmd.extend(["--accept-source-agreements", "--accept-package-agreements"])
                
            self.logger.info(f"Upgrading package: {package_id}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                message = f"Successfully upgraded {package_id}"
                self.logger.info(message)
                return True, message
            else:
                error_msg = f"Upgrade failed: {result.stderr}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"Upgrade timeout for {package_id}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Upgrade error: {e}"
            self.logger.error(error_msg)
            return False, error_msg


# Safe package whitelist for common applications
SAFE_PACKAGES = {
    "7zip.7zip": "7-Zip",
    "Mozilla.Firefox": "Firefox",
    "Google.Chrome": "Chrome",
    "Microsoft.VisualStudioCode": "VS Code",
    "Notepad++.Notepad++": "Notepad++",
    "VideoLAN.VLC": "VLC Media Player",
    "Adobe.Acrobat.Reader.64-bit": "Adobe Reader",
    "Git.Git": "Git",
    "Python.Python.3.11": "Python 3.11",
    "Microsoft.PowerToys": "PowerToys"
}


def is_safe_package(package_id: str) -> bool:
    """Check if a package is in the safe whitelist."""
    return package_id in SAFE_PACKAGES


def get_safe_package_name(package_id: str) -> Optional[str]:
    """Get friendly name for a safe package."""
    return SAFE_PACKAGES.get(package_id)