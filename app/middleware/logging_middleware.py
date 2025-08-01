import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import get_logger, log_request, log_response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming requests and responses"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("middleware")
    
    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()
        
        # Extract request details
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else None
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Log request
        request_data = {
            "client_ip": client_ip,
            "user_agent": user_agent,
        }
        if query_params:
            request_data["query_params"] = query_params
            
        log_request(self.logger, method, path, **request_data)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful response
            log_response(
                self.logger, 
                method, 
                path, 
                response.status_code, 
                duration_ms,
                client_ip=client_ip
            )
            
            return response
            
        except Exception as e:
            # Calculate duration for failed requests
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error response
            self.logger.error(
                f"{method} {path} - Error ({duration_ms:.2f}ms)",
                extra={
                    "event_type": "request_error",
                    "http_method": method,
                    "path": path,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "client_ip": client_ip
                },
                exc_info=True
            )
            
            # Re-raise the exception
            raise