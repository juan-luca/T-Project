"""
Cyber Command Center - Error Handlers & Response Utilities
Centralized error handling and consistent API responses
"""
import traceback
from functools import wraps
from flask import jsonify, request
from datetime import datetime
import psutil


# Error codes
class ErrorCodes:
    # Client errors (4xx)
    BAD_REQUEST = "BAD_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMITED = "RATE_LIMITED"
    CONFLICT = "CONFLICT"
    
    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"


class APIError(Exception):
    """Custom API Error with code, message, and HTTP status"""
    
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self, include_details: bool = False):
        error = {
            'code': self.code,
            'message': self.message
        }
        if include_details and self.details:
            error['details'] = self.details
        return error


# Pre-defined errors for convenience
class Errors:
    @staticmethod
    def bad_request(message: str = "Bad request", details: dict = None):
        return APIError(ErrorCodes.BAD_REQUEST, message, 400, details)
    
    @staticmethod
    def not_found(resource: str = "Resource"):
        return APIError(ErrorCodes.NOT_FOUND, f"{resource} not found", 404)
    
    @staticmethod
    def validation_error(message: str = "Validation failed", details: dict = None):
        return APIError(ErrorCodes.VALIDATION_ERROR, message, 400, details)
    
    @staticmethod
    def unauthorized(message: str = "Authentication required"):
        return APIError(ErrorCodes.UNAUTHORIZED, message, 401)
    
    @staticmethod
    def forbidden(message: str = "Access denied"):
        return APIError(ErrorCodes.FORBIDDEN, message, 403)
    
    @staticmethod
    def rate_limited(message: str = "Rate limit exceeded"):
        return APIError(ErrorCodes.RATE_LIMITED, message, 429)
    
    @staticmethod
    def internal_error(message: str = "Internal server error"):
        return APIError(ErrorCodes.INTERNAL_ERROR, message, 500)
    
    @staticmethod
    def database_error(message: str = "Database error"):
        return APIError(ErrorCodes.DATABASE_ERROR, message, 500)
    
    @staticmethod
    def dependency_error(dependency: str, message: str = None):
        msg = message or f"Required dependency '{dependency}' is not available"
        return APIError(ErrorCodes.DEPENDENCY_ERROR, msg, 503)


def success_response(data=None, message: str = None, status_code: int = 200):
    """
    Create a successful API response
    
    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code
    
    Returns:
        Flask response tuple
    """
    response = {'success': True}
    
    if message:
        response['message'] = message
    
    if data is not None:
        if isinstance(data, dict):
            response.update(data)
        else:
            response['data'] = data
    
    return jsonify(response), status_code


def error_response(error: APIError = None, code: str = None, message: str = None, 
                  status_code: int = 400, details: dict = None):
    """
    Create an error API response
    
    Args:
        error: APIError instance
        code: Error code (if not using APIError)
        message: Error message (if not using APIError)
        status_code: HTTP status code
        details: Additional error details
    
    Returns:
        Flask response tuple
    """
    if error:
        response = {
            'success': False,
            'error': error.to_dict(include_details=True)
        }
        return jsonify(response), error.status_code
    
    response = {
        'success': False,
        'error': {
            'code': code or ErrorCodes.INTERNAL_ERROR,
            'message': message or "An error occurred"
        }
    }
    
    if details:
        response['error']['details'] = details
    
    return jsonify(response), status_code


def register_error_handlers(app, debug_mode: bool = False):
    """
    Register global error handlers for a Flask app
    
    Args:
        app: Flask application instance
        debug_mode: Include stack traces in responses
    """
    from core.logger import error_logger, app_logger
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors"""
        app_logger.warning(f"API Error: {error.code} - {error.message}")
        return error_response(error)
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle bad request errors"""
        return error_response(
            code=ErrorCodes.BAD_REQUEST,
            message="Bad request",
            status_code=400
        )
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle not found errors"""
        path = request.path
        return error_response(
            code=ErrorCodes.NOT_FOUND,
            message=f"Resource not found: {path}",
            status_code=404
        )
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle method not allowed errors"""
        return error_response(
            code=ErrorCodes.BAD_REQUEST,
            message=f"Method {request.method} not allowed for {request.path}",
            status_code=405
        )
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle internal server errors"""
        error_logger.error(f"Internal error: {str(error)}", exc_info=True)
        
        details = None
        if debug_mode:
            details = {
                'exception': str(error),
                'traceback': traceback.format_exc()
            }
        
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message="Internal server error",
            status_code=500,
            details=details
        )
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unexpected exceptions"""
        error_logger.error(f"Unexpected error: {type(error).__name__}: {str(error)}", exc_info=True)
        
        details = None
        if debug_mode:
            details = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': traceback.format_exc()
            }
        
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message="An unexpected error occurred",
            status_code=500,
            details=details
        )
    
    app_logger.info("Error handlers registered")


def handle_errors(func):
    """
    Decorator to wrap route functions with error handling
    
    Usage:
        @app.route('/api/example')
        @handle_errors
        def my_endpoint():
            # Code that might raise exceptions
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            return error_response(e)
        except Exception as e:
            from core.logger import error_logger
            error_logger.error(f"Unhandled error in {func.__name__}: {str(e)}", exc_info=True)
            return error_response(
                code=ErrorCodes.INTERNAL_ERROR,
                message="An error occurred processing your request",
                status_code=500
            )
    return wrapper


# Rate limiting (simple in-memory implementation)
_rate_limit_store = {}

def rate_limit(requests_per_minute: int = 60, per_ip: bool = True):
    """
    Simple rate limiting decorator
    
    Args:
        requests_per_minute: Maximum requests allowed per minute
        per_ip: Rate limit per IP address
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = request.remote_addr if per_ip else "global"
            now = datetime.now()
            
            # Clean old entries
            if key in _rate_limit_store:
                _rate_limit_store[key] = [
                    t for t in _rate_limit_store[key]
                    if (now - t).total_seconds() < 60
                ]
            else:
                _rate_limit_store[key] = []
            
            # Check limit
            if len(_rate_limit_store[key]) >= requests_per_minute:
                return error_response(
                    error=Errors.rate_limited(
                        f"Rate limit exceeded. Maximum {requests_per_minute} requests per minute."
                    )
                )
            
            # Record this request
            _rate_limit_store[key].append(now)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Health Check
class HealthChecker:
    """System health checker"""
    
    _start_time = datetime.now()
    _version = "1.0.0"
    
    @classmethod
    def get_health_status(cls) -> dict:
        """Get comprehensive health status"""
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database check
        db_status = cls._check_database()
        
        # Calculate uptime
        uptime_seconds = (datetime.now() - cls._start_time).total_seconds()
        
        # Determine overall status
        overall_status = "healthy"
        if not db_status['connected']:
            overall_status = "degraded"
        if cpu_percent > 90 or memory.percent > 90:
            overall_status = "warning"
        
        return {
            'status': overall_status,
            'version': cls._version,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'uptime': {
                'seconds': int(uptime_seconds),
                'human': cls._format_uptime(uptime_seconds)
            },
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'percent': round(disk.percent, 1)
                }
            },
            'services': {
                'database': db_status,
                'network_scanner': {'status': 'available'},
                'websocket': {'status': 'available'}
            }
        }
    
    @classmethod
    def _check_database(cls) -> dict:
        """Check database connectivity"""
        try:
            from database.models import get_session, Device
            session = get_session()
            # Simple query to test connection
            session.query(Device).first()
            session.close()
            return {'connected': True, 'status': 'available'}
        except Exception as e:
            return {'connected': False, 'status': 'unavailable', 'error': str(e)}
    
    @classmethod
    def _format_uptime(cls, seconds: float) -> str:
        """Format uptime in human readable format"""
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        
        return " ".join(parts)
