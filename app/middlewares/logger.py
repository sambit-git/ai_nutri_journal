import logging
import time
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware  # Updated import path
from starlette.types import ASGIApp
import json
import uuid

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Log request details
        await self.log_request(request, request_id)
        
        start_time = time.time()
        
        try:
            # Call the next middleware/route handler
            response = await call_next(request)
        except Exception as e:
            # Log unhandled exceptions
            logger.error(f"Request ID: {request_id} - Unhandled exception: {str(e)}", exc_info=True)
            raise
        
        # Calculate processing time
        process_time = (time.time() - start_time) * 1000
        
        # Log response details
        await self.log_response(request, response, process_time, request_id)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    async def log_request(self, request: Request, request_id: str) -> None:
        """Log incoming request details"""
        try:
            body = await request.body()
            try:
                body = json.loads(body.decode()) if body else None
            except (json.JSONDecodeError, UnicodeDecodeError):
                body = body.decode() if body else None
            
            # Filter sensitive headers
            headers = dict(request.headers)
            sensitive_headers = ['authorization', 'cookie', 'set-cookie']
            for header in sensitive_headers:
                if header in headers:
                    headers[header] = '*****'
            
            request_log = {
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "headers": headers,
                "query_params": dict(request.query_params),
                "client": request.client.host if request.client else None,
                "body": body
            }
            
            logger.info(
                f"Incoming request\n{json.dumps(request_log, indent=2, default=str)}"
            )
            
        except Exception as e:
            logger.error(f"Failed to log request: {str(e)}", exc_info=True)

    async def log_response(
        self, 
        request: Request, 
        response: Response, 
        process_time: float, 
        request_id: str
    ) -> None:
        """Log response details including body"""
        try:
            # Get response body if exists
            response_body = None
            if hasattr(response, "body"):
                body = response.body
                if isinstance(body, bytes):
                    try:
                        response_body = json.loads(body.decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        response_body = "<binary-data>"
                else:
                    response_body = body
            
            response_log = {
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": f"{process_time:.2f}ms",
                "headers": dict(response.headers),
                "body": response_body
            }
            
            logger.info(
                f"Request completed\n{json.dumps(response_log, indent=2, default=str)}"
            )
        except Exception as e:
            logger.error(f"Failed to log response: {str(e)}", exc_info=True)


class LoggingRoute(APIRoute):
    """Custom route class for additional route-specific logging"""
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        
        async def custom_route_handler(request: Request) -> Response:
            # Before request handling
            logger.info(
                f"Routing to {self.path} with method {self.methods}",
                extra={"request_id": request.headers.get("X-Request-ID", "unknown")}
            )
            
            response = await original_route_handler(request)
            return response
        
        return custom_route_handler