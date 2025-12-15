"""
Input validators for the secure P2P messenger.
Validates IP addresses, ports, and other user inputs.
"""

import re
import ipaddress


def validate_ip(ip_string):
    """
    Validate IP address format.
    
    Args:
        ip_string: String to validate as IP address
        
    Returns:
        bool: True if valid IP address
    """
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False


def validate_port(port):
    """
    Validate port number.
    
    Args:
        port: Port number to validate (int or string)
        
    Returns:
        bool: True if valid port (1-65535)
    """
    try:
        port_int = int(port)
        return 1 <= port_int <= 65535
    except (ValueError, TypeError):
        return False


def validate_message_length(message, max_length=10000):
    """
    Validate message length.
    
    Args:
        message: Message string to validate
        max_length: Maximum allowed length
        
    Returns:
        bool: True if message length is acceptable
    """
    return len(message) <= max_length


def validate_filename(filename):
    """
    Validate filename for security.
    
    Args:
        filename: Filename to validate
        
    Returns:
        bool: True if filename is safe
    """
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    
    # Check for valid characters
    valid_pattern = re.compile(r'^[\w\-. ]+$')
    return bool(valid_pattern.match(filename))


def validate_file_size(size, max_size=10485760):
    """
    Validate file size.
    
    Args:
        size: File size in bytes
        max_size: Maximum allowed size (default 10MB)
        
    Returns:
        bool: True if file size is acceptable
    """
    return 0 < size <= max_size


def sanitize_input(text):
    """
    Sanitize text input.
    
    Args:
        text: Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if text is None:
        return ""
    return str(text).strip()
