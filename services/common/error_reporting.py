"""
Enhanced error reporting with Sentry integration
"""
import os
import logging
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
import json

try:
    import sentry_sdk
    from sentry_sdk import capture_exception, set_user, set_tag, set_context
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    sentry_sdk = None


class ErrorReporter:
    """Enhanced error reporting with Sentry and structured logging"""
    
    def __init__(self, service_name: str, sentry_dsn: Optional[str] = None):
        self.service_name = service_name
        self.logger = logging.getLogger(f"{service_name}.ErrorReporter")
        
        # Initialize Sentry if DSN is provided
        if SENTRY_AVAILABLE and (sentry_dsn or os.getenv('SENTRY_DSN')):
            sentry_sdk.init(
                dsn=sentry_dsn or os.getenv('SENTRY_DSN'),
                environment=os.getenv('ENVIRONMENT', 'development'),
                traces_sample_rate=1.0,
                attach_stacktrace=True,
                send_default_pii=False,
                before_send=self._before_send_filter
            )
            set_tag("service", service_name)
            self.logger.info("Sentry error reporting initialized")
        else:
            self.logger.warning("Sentry not available or DSN not provided")
    
    def _before_send_filter(self, event, hint):
        """Filter sensitive data before sending to Sentry"""
        # Remove sensitive data from the event
        if 'request' in event and 'data' in event['request']:
            # Redact sensitive fields
            sensitive_fields = ['password', 'token', 'api_key', 'secret']
            for field in sensitive_fields:
                if field in event['request']['data']:
                    event['request']['data'][field] = '[REDACTED]'
        
        return event
    
    def report_error(self, 
                    error: Exception, 
                    context: Optional[Dict[str, Any]] = None,
                    user_info: Optional[Dict[str, Any]] = None,
                    level: str = "error"):
        """
        Report an error with context
        
        Args:
            error: The exception to report
            context: Additional context information
            user_info: User information (id, email, etc.)
            level: Error level (debug, info, warning, error, critical)
        """
        # Create error record
        error_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "level": level
        }
        
        # Log the error
        log_method = getattr(self.logger, level, self.logger.error)
        log_method(f"Error reported: {json.dumps(error_record, indent=2)}")
        
        # Send to Sentry if available
        if SENTRY_AVAILABLE and sentry_sdk.Hub.current.client:
            # Set user context if provided
            if user_info:
                set_user(user_info)
            
            # Set additional context
            if context:
                for key, value in context.items():
                    set_context(key, value)
            
            # Capture the exception
            capture_exception(error)
    
    def report_performance_issue(self, 
                                operation: str, 
                                duration: float, 
                                threshold: float,
                                context: Optional[Dict[str, Any]] = None):
        """
        Report performance issues
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            threshold: Expected threshold in seconds
            context: Additional context
        """
        if duration > threshold:
            perf_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "service": self.service_name,
                "operation": operation,
                "duration": duration,
                "threshold": threshold,
                "exceeded_by": duration - threshold,
                "context": context or {}
            }
            
            self.logger.warning(f"Performance issue: {json.dumps(perf_record, indent=2)}")
            
            # Send to Sentry as a custom event
            if SENTRY_AVAILABLE and sentry_sdk.Hub.current.client:
                with sentry_sdk.push_scope() as scope:
                    scope.set_tag("type", "performance")
                    scope.set_context("performance", perf_record)
                    sentry_sdk.capture_message(
                        f"Performance threshold exceeded for {operation}",
                        level="warning"
                    )
    
    def create_error_context(self, request_id: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Create a standard error context"""
        return {
            "request_id": request_id,
            "endpoint": endpoint,
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }


class ErrorMiddleware:
    """Middleware for automatic error tracking"""
    
    def __init__(self, error_reporter: ErrorReporter):
        self.error_reporter = error_reporter
    
    async def __call__(self, request, call_next):
        """Process the request and catch any errors"""
        import uuid
        from fastapi import Request
        from fastapi.responses import JSONResponse
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Create error context
            context = self.error_reporter.create_error_context(
                request_id=request_id,
                endpoint=str(request.url),
                method=request.method,
                headers=dict(request.headers)
            )
            
            # Report the error
            self.error_reporter.report_error(
                error=e,
                context=context,
                level="critical" if isinstance(e, SystemError) else "error"
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "message": "An error has been logged and reported"
                }
            )