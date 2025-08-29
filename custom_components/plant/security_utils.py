"""Security utilities for plant integration."""

import os
import re
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional
import logging

_LOGGER = logging.getLogger(__name__)

# Allowed URL schemes for image downloads
ALLOWED_URL_SCHEMES = {"http", "https"}

# Allowed file extensions for images
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# Maximum filename length
MAX_FILENAME_LENGTH = 255

# Pattern for safe entity IDs (alphanumeric, underscore, dot, hyphen)
SAFE_ENTITY_ID_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')


def validate_and_sanitize_filename(filename: str) -> Optional[str]:
    """
    Validate and sanitize filename to prevent path traversal attacks.
    
    Args:
        filename: The filename to validate
        
    Returns:
        Sanitized filename or None if invalid
    """
    if not filename:
        return None
        
    # Remove any directory separators and null bytes
    sanitized = filename.replace('/', '').replace('\\', '').replace('\0', '')
    
    # Remove leading dots to prevent hidden files
    sanitized = sanitized.lstrip('.')
    
    # Check length
    if len(sanitized) > MAX_FILENAME_LENGTH:
        sanitized = sanitized[:MAX_FILENAME_LENGTH]
    
    # Ensure it's not empty after sanitization
    if not sanitized:
        return None
        
    # Check for valid characters only
    if not re.match(r'^[a-zA-Z0-9._-]+$', sanitized):
        # Remove invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', sanitized)
    
    return sanitized


def validate_download_path(path: str, base_path: str) -> bool:
    """
    Validate that download path is within allowed base directory.
    
    Args:
        path: The path to validate
        base_path: The allowed base directory
        
    Returns:
        True if path is safe, False otherwise
    """
    try:
        # Resolve both paths to absolute paths
        abs_path = Path(path).resolve()
        abs_base = Path(base_path).resolve()
        
        # Check if path is within base directory
        return abs_base in abs_path.parents or abs_path == abs_base
        
    except (OSError, ValueError):
        return False


def validate_image_url(url: str) -> bool:
    """
    Validate image URL for security.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if URL is safe, False otherwise
    """
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ALLOWED_URL_SCHEMES:
            _LOGGER.warning("Invalid URL scheme: %s", parsed.scheme)
            return False
            
        # Check for localhost/private IPs (basic protection)
        if parsed.hostname:
            # Block localhost and common private ranges
            blocked_hosts = {
                'localhost', '127.0.0.1', '0.0.0.0',
                # Add more as needed
            }
            if parsed.hostname.lower() in blocked_hosts:
                _LOGGER.warning("Blocked hostname: %s", parsed.hostname)
                return False
                
            # Block private IP ranges (basic check)
            if (parsed.hostname.startswith('192.168.') or 
                parsed.hostname.startswith('10.') or
                parsed.hostname.startswith('172.')):
                _LOGGER.warning("Private IP address blocked: %s", parsed.hostname)
                return False
        
        return True
        
    except Exception as e:
        _LOGGER.error("URL validation error: %s", e)
        return False


def sanitize_entity_id(entity_id: str) -> Optional[str]:
    """
    Sanitize entity ID to prevent injection attacks.
    
    Args:
        entity_id: The entity ID to sanitize
        
    Returns:
        Sanitized entity ID or None if invalid
    """
    if not entity_id:
        return None
        
    # Basic validation - entity IDs should follow HA patterns
    if not SAFE_ENTITY_ID_PATTERN.match(entity_id):
        _LOGGER.warning("Invalid entity ID format: %s", entity_id)
        return None
        
    # Additional length check
    if len(entity_id) > 255:
        _LOGGER.warning("Entity ID too long: %s", entity_id)
        return None
        
    return entity_id


def secure_file_path(download_path: str, entity_id: str, timestamp: str, extension: str = ".jpg") -> Optional[str]:
    """
    Create a secure file path for image downloads.
    
    Args:
        download_path: Base download directory
        entity_id: Entity ID (will be sanitized)
        timestamp: Timestamp string
        extension: File extension (will be validated)
        
    Returns:
        Secure file path or None if validation fails
    """
    # Sanitize inputs
    safe_entity_id = sanitize_entity_id(entity_id)
    if not safe_entity_id:
        return None
        
    # Validate extension
    if extension.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        _LOGGER.warning("Invalid file extension: %s", extension)
        return None
        
    # Create safe filename
    safe_filename = f"{safe_entity_id}_{timestamp}{extension}"
    safe_filename = validate_and_sanitize_filename(safe_filename)
    
    if not safe_filename:
        return None
        
    # Create full path
    full_path = os.path.join(download_path, safe_filename)
    
    # Validate path is within download directory
    if not validate_download_path(full_path, download_path):
        _LOGGER.error("Path traversal attempt blocked: %s", full_path)
        return None
        
    return full_path


class SecurityError(Exception):
    """Custom exception for security-related errors."""
    pass