"""
Cyber Command Center - Input Validation & Sanitization
Security-focused validators for all user inputs
"""
import re
import ipaddress
from typing import Optional, Tuple, Any, List
from functools import wraps
from flask import request, jsonify


class ValidationError(Exception):
    """Custom validation error with code and message"""
    def __init__(self, code: str, message: str, field: str = None):
        self.code = code
        self.message = message
        self.field = field
        super().__init__(message)


class Validators:
    """Collection of validation functions"""
    
    # Regex patterns
    IP_PATTERN = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    MAC_PATTERN = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    HOSTNAME_PATTERN = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$')
    SAFE_STRING_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\s\.]+$')
    
    # Dangerous patterns to block
    COMMAND_INJECTION_PATTERNS = [
        r'[;&|`$]',  # Shell metacharacters
        r'\$\(',     # Command substitution
        r'`',        # Backtick command substitution
        r'\.\.',     # Path traversal
        r'<script',  # XSS
        r'javascript:', # XSS
        r'on\w+=',   # Event handlers
    ]
    
    @classmethod
    def validate_ip(cls, ip: str, allow_private: bool = True) -> Tuple[bool, str]:
        """
        Validate IP address format and optionally check if it's private
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not ip:
            return False, "IP address is required"
        
        ip = str(ip).strip()
        
        if not cls.IP_PATTERN.match(ip):
            return False, f"Invalid IP address format: {ip}"
        
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            if not allow_private and ip_obj.is_private:
                return False, "Private IP addresses not allowed"
            
            if ip_obj.is_multicast:
                return False, "Multicast addresses not allowed"
            
            if ip_obj.is_reserved and str(ip) not in ['0.0.0.0', '255.255.255.255']:
                return False, "Reserved addresses not allowed"
            
            return True, ""
        except ValueError as e:
            return False, f"Invalid IP address: {str(e)}"
    
    @classmethod
    def validate_mac(cls, mac: str) -> Tuple[bool, str]:
        """
        Validate MAC address format
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not mac:
            return False, "MAC address is required"
        
        mac = str(mac).strip().upper()
        
        # Normalize separators
        mac = mac.replace('-', ':')
        
        if not cls.MAC_PATTERN.match(mac):
            return False, f"Invalid MAC address format: {mac}"
        
        return True, ""
    
    @classmethod
    def validate_hostname(cls, hostname: str, max_length: int = 255) -> Tuple[bool, str]:
        """
        Validate hostname format
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not hostname:
            return True, ""  # Hostname is optional
        
        hostname = str(hostname).strip()
        
        if len(hostname) > max_length:
            return False, f"Hostname too long (max {max_length} chars)"
        
        if not cls.HOSTNAME_PATTERN.match(hostname):
            return False, f"Invalid hostname format: {hostname}"
        
        return True, ""
    
    @classmethod
    def validate_port(cls, port: Any, allow_zero: bool = False) -> Tuple[bool, str]:
        """
        Validate port number
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            port = int(port)
        except (ValueError, TypeError):
            return False, "Port must be a number"
        
        min_port = 0 if allow_zero else 1
        if port < min_port or port > 65535:
            return False, f"Port must be between {min_port} and 65535"
        
        return True, ""
    
    @classmethod
    def validate_port_range(cls, ports: str) -> Tuple[bool, str, List[int]]:
        """
        Validate and parse port range (e.g., "80,443,8000-8100")
        
        Returns:
            Tuple of (is_valid, error_message, parsed_ports)
        """
        if not ports:
            return True, "", []
        
        parsed = []
        
        try:
            parts = str(ports).split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    start, end = part.split('-', 1)
                    start, end = int(start), int(end)
                    if start > end:
                        return False, f"Invalid range: {start}-{end}", []
                    if end - start > 1000:
                        return False, "Port range too large (max 1000 ports)", []
                    parsed.extend(range(start, end + 1))
                else:
                    parsed.append(int(part))
            
            # Validate all ports
            for p in parsed:
                if p < 1 or p > 65535:
                    return False, f"Invalid port: {p}", []
            
            return True, "", list(set(parsed))  # Remove duplicates
        except ValueError:
            return False, f"Invalid port format: {ports}", []
    
    @classmethod
    def sanitize_string(cls, text: str, max_length: int = 500, 
                       allow_special: bool = False) -> str:
        """
        Sanitize a string by removing potentially dangerous characters
        
        Args:
            text: Input string
            max_length: Maximum allowed length
            allow_special: Allow some special characters
        
        Returns:
            Sanitized string
        """
        if not text:
            return ""
        
        text = str(text).strip()
        
        # Check for command injection patterns
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                # Remove the dangerous parts
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Truncate
        text = text[:max_length]
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        if not allow_special:
            # Keep only safe characters
            text = re.sub(r'[^\w\s\.\-]', '', text)
        
        return text.strip()
    
    @classmethod
    def validate_json_field(cls, data: dict, field: str, 
                           field_type: type = str, 
                           required: bool = True,
                           default: Any = None) -> Tuple[bool, str, Any]:
        """
        Validate a field from JSON data
        
        Returns:
            Tuple of (is_valid, error_message, value)
        """
        value = data.get(field, default)
        
        if value is None or value == "":
            if required:
                return False, f"Field '{field}' is required", None
            return True, "", default
        
        if not isinstance(value, field_type):
            try:
                value = field_type(value)
            except (ValueError, TypeError):
                return False, f"Field '{field}' must be {field_type.__name__}", None
        
        return True, "", value
    
    @classmethod
    def check_command_injection(cls, text: str) -> bool:
        """
        Check if text contains potential command injection
        
        Returns:
            True if dangerous patterns found
        """
        if not text:
            return False
        
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False


def validate_request(*validations):
    """
    Decorator for validating request parameters
    
    Usage:
        @validate_request(
            ('ip', 'ip', True),      # (field_name, validator_type, required)
            ('mac', 'mac', False),
            ('port', 'port', False)
        )
        def my_endpoint():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.json or {}
            errors = []
            
            for field_name, validator_type, required in validations:
                value = data.get(field_name)
                
                if not value and required:
                    errors.append({
                        'field': field_name,
                        'code': 'REQUIRED',
                        'message': f"Field '{field_name}' is required"
                    })
                    continue
                
                if not value:
                    continue
                
                # Apply appropriate validator
                if validator_type == 'ip':
                    is_valid, msg = Validators.validate_ip(value)
                elif validator_type == 'mac':
                    is_valid, msg = Validators.validate_mac(value)
                elif validator_type == 'hostname':
                    is_valid, msg = Validators.validate_hostname(value)
                elif validator_type == 'port':
                    is_valid, msg = Validators.validate_port(value)
                elif validator_type == 'safe_string':
                    is_valid = not Validators.check_command_injection(value)
                    msg = "Potentially dangerous characters detected" if not is_valid else ""
                else:
                    is_valid, msg = True, ""
                
                if not is_valid:
                    errors.append({
                        'field': field_name,
                        'code': 'INVALID',
                        'message': msg
                    })
            
            if errors:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Request validation failed',
                        'details': errors
                    }
                }), 400
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Convenience functions
def is_valid_ip(ip: str) -> bool:
    """Quick check if IP is valid"""
    return Validators.validate_ip(ip)[0]

def is_valid_mac(mac: str) -> bool:
    """Quick check if MAC is valid"""
    return Validators.validate_mac(mac)[0]

def sanitize(text: str, max_length: int = 500) -> str:
    """Quick sanitize function"""
    return Validators.sanitize_string(text, max_length)

def normalize_mac(mac: str) -> str:
    """Normalize MAC address to uppercase with colons"""
    if not mac:
        return ""
    return mac.strip().upper().replace('-', ':')

def normalize_ip(ip: str) -> str:
    """Normalize IP address"""
    if not ip:
        return ""
    try:
        return str(ipaddress.ip_address(ip.strip()))
    except:
        return ip.strip()
