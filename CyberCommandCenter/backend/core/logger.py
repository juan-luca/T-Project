"""
Cyber Command Center - Advanced Logging System
Centralized logging with file rotation, colored console output, and structured logs
"""
import logging
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from functools import wraps
import traceback

# Log directory
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Log files
APP_LOG = LOG_DIR / "app.log"
ERROR_LOG = LOG_DIR / "error.log"
AUDIT_LOG = LOG_DIR / "audit.log"
ACCESS_LOG = LOG_DIR / "access.log"

# Colors for console output (Windows/Linux compatible)
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"

# Enable colors in Windows terminal
if sys.platform == 'win32':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BOLD + Colors.RED,
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelno, Colors.WHITE)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format level name
        levelname = record.levelname
        if record.levelno == logging.DEBUG:
            levelname = "DEBUG"
        elif record.levelno == logging.INFO:
            levelname = "INFO "
        elif record.levelno == logging.WARNING:
            levelname = "WARN "
        elif record.levelno == logging.ERROR:
            levelname = "ERROR"
        elif record.levelno == logging.CRITICAL:
            levelname = "CRIT "
        
        # Build message
        msg = f"{Colors.WHITE}[{timestamp}]{Colors.RESET} {color}{levelname}{Colors.RESET} "
        msg += f"{Colors.MAGENTA}{record.name.split('.')[-1][:12]:<12}{Colors.RESET} "
        msg += f"{record.getMessage()}"
        
        return msg


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }
        
        # Add extra data if present
        if hasattr(record, 'extra_data'):
            log_data['data'] = record.extra_data
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data, default=str)


def setup_logger(name: str, log_file: Path = None, level: int = logging.INFO, json_format: bool = False) -> logging.Logger:
    """
    Configure and return a logger instance
    
    Args:
        name: Logger name
        log_file: Optional file path for logging
        level: Logging level
        json_format: Use JSON format for file logs
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    console_handler.setLevel(level)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        if json_format:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
            ))
        
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    
    return logger


# Pre-configured loggers
app_logger = setup_logger('CyberCommand', APP_LOG, logging.DEBUG)
error_logger = setup_logger('CyberCommand.Error', ERROR_LOG, logging.ERROR, json_format=True)
audit_logger = setup_logger('CyberCommand.Audit', AUDIT_LOG, logging.INFO, json_format=True)
access_logger = setup_logger('CyberCommand.Access', ACCESS_LOG, logging.INFO)


class AuditLogger:
    """Audit logger for tracking security-relevant events"""
    
    @staticmethod
    def log(action: str, details: dict = None, user: str = "anonymous", success: bool = True):
        """
        Log an audit event
        
        Args:
            action: Action performed (e.g., "device_scan", "prank_executed")
            details: Additional details about the action
            user: User who performed the action
            success: Whether the action succeeded
        """
        record = audit_logger.makeRecord(
            name='CyberCommand.Audit',
            level=logging.INFO,
            fn='',
            lno=0,
            msg=f"ACTION: {action} | USER: {user} | SUCCESS: {success}",
            args=(),
            exc_info=None
        )
        record.extra_data = {
            'action': action,
            'user': user,
            'success': success,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        audit_logger.handle(record)


class RequestLogger:
    """Logger for HTTP requests"""
    
    @staticmethod
    def log_request(method: str, path: str, status_code: int, duration_ms: float, 
                    client_ip: str = None, user_agent: str = None):
        """Log an HTTP request"""
        status_color = Colors.GREEN if status_code < 400 else Colors.YELLOW if status_code < 500 else Colors.RED
        
        msg = f"{method:6} {path:50} {status_color}{status_code}{Colors.RESET} {duration_ms:.2f}ms"
        if client_ip:
            msg += f" | {client_ip}"
        
        access_logger.info(msg)


def log_function_call(logger_instance=None):
    """
    Decorator to log function calls
    
    Usage:
        @log_function_call()
        def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger_instance or app_logger
            func_name = func.__name__
            
            # Log entry
            log.debug(f"→ {func_name}() called with args={len(args)}, kwargs={list(kwargs.keys())}")
            
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                log.debug(f"← {func_name}() completed in {duration:.2f}ms")
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                log.error(f"✗ {func_name}() failed after {duration:.2f}ms: {str(e)}")
                raise
        
        return wrapper
    return decorator


# Convenience functions
def debug(msg, *args, **kwargs):
    app_logger.debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    app_logger.info(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    app_logger.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    app_logger.error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    app_logger.critical(msg, *args, **kwargs)

def audit(action, details=None, user="anonymous", success=True):
    AuditLogger.log(action, details, user, success)


# Log startup message
app_logger.info("╔═══════════════════════════════════════════════════════╗")
app_logger.info("║       CYBER COMMAND CENTER - Logging Initialized      ║")
app_logger.info("╚═══════════════════════════════════════════════════════╝")
