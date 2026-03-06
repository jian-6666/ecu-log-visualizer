"""
Error Handler Module

This module provides global exception handling middleware and utilities
for the ECU Log Visualizer API. It ensures consistent error responses,
proper logging, and prevents exposure of internal implementation details.

Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
"""

import logging
import traceback
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_request_id() -> str:
    """Generate a unique request ID for tracking"""
    return f"req-{uuid.uuid4().hex[:16]}"


def create_error_response(
    error_code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response
    
    Args:
        error_code: Error code identifier
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional details
        request_id: Optional request ID for tracking
        
    Returns:
        Standardized error response dictionary
    """
    response = {
        "error_code": error_code,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if details:
        response["details"] = details
    
    if request_id:
        response["details"] = response.get("details", {})
        response["details"]["request_id"] = request_id
    
    return response


def log_error(
    request_id: str,
    endpoint: str,
    method: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> None:
    """
    Log error details for debugging and monitoring
    
    Args:
        request_id: Unique request identifier
        endpoint: API endpoint path
        method: HTTP method
        error_type: Type of error
        error_message: Error message
        stack_trace: Optional stack trace
        user_agent: Optional user agent string
        ip_address: Optional client IP address
    """
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "ERROR",
        "request_id": request_id,
        "endpoint": endpoint,
        "method": method,
        "error_type": error_type,
        "error_message": error_message,
        "user_agent": user_agent,
        "ip_address": ip_address
    }
    
    if stack_trace:
        log_data["stack_trace"] = stack_trace
    
    logger.error(f"Error occurred: {log_data}")


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions (404, 400, etc.)
    
    Args:
        request: FastAPI request object
        exc: HTTP exception
        
    Returns:
        JSONResponse with standardized error format
        
    Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
    """
    request_id = generate_request_id()
    
    # Extract error details from exception
    if isinstance(exc.detail, dict):
        # Detail is already a structured error response
        error_response = exc.detail
        if "details" not in error_response:
            error_response["details"] = {}
        error_response["details"]["request_id"] = request_id
    else:
        # Detail is a simple string
        error_code = "HTTP_ERROR"
        if exc.status_code == 404:
            error_code = "NOT_FOUND"
        elif exc.status_code == 400:
            error_code = "BAD_REQUEST"
        elif exc.status_code == 413:
            error_code = "PAYLOAD_TOO_LARGE"
        elif exc.status_code == 415:
            error_code = "UNSUPPORTED_MEDIA_TYPE"
        
        error_response = create_error_response(
            error_code=error_code,
            message=str(exc.detail),
            status_code=exc.status_code,
            request_id=request_id
        )
    
    # Log the error
    log_error(
        request_id=request_id,
        endpoint=request.url.path,
        method=request.method,
        error_type=f"HTTPException_{exc.status_code}",
        error_message=str(exc.detail),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle request validation errors (invalid parameters)
    
    Args:
        request: FastAPI request object
        exc: Validation error exception
        
    Returns:
        JSONResponse with standardized error format
        
    Validates: Requirements 8.5
    """
    request_id = generate_request_id()
    
    # Extract validation error details
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = create_error_response(
        error_code="VALIDATION_ERROR",
        message="Request validation failed. Please check the provided parameters.",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={
            "validation_errors": validation_errors,
            "request_id": request_id
        }
    )
    
    # Log the validation error
    log_error(
        request_id=request_id,
        endpoint=request.url.path,
        method=request.method,
        error_type="ValidationError",
        error_message=f"Validation failed: {validation_errors}",
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions (500 errors)
    
    This handler catches any unexpected exceptions and returns a safe
    error response without exposing internal implementation details.
    
    Args:
        request: FastAPI request object
        exc: Exception
        
    Returns:
        JSONResponse with standardized error format
        
    Validates: Requirements 8.6, 8.7
    """
    request_id = generate_request_id()
    
    # Get stack trace for logging (but don't expose it to the client)
    stack_trace = traceback.format_exc()
    
    # Log the error with full details
    log_error(
        request_id=request_id,
        endpoint=request.url.path,
        method=request.method,
        error_type=type(exc).__name__,
        error_message=str(exc),
        stack_trace=stack_trace,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    
    # Return a safe error response without internal details
    error_response = create_error_response(
        error_code="INTERNAL_ERROR",
        message="An internal error occurred while processing your request. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={
            "request_id": request_id
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )


def setup_exception_handlers(app) -> None:
    """
    Register all exception handlers with the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    # Handle HTTP exceptions (404, 400, etc.)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Handle validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Handle all other exceptions
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered successfully")
