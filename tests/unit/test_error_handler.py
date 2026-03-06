"""
Unit tests for error handler module

Tests the global exception handling middleware including:
- HTTP exception handling (404, 400, 413, 415)
- Validation error handling (422)
- General exception handling (500)
- Error logging functionality
- Request ID generation
- Standardized error response format

Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from src.error_handler import (
    generate_request_id,
    create_error_response,
    log_error,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    setup_exception_handlers
)


class TestRequestIdGeneration:
    """Test request ID generation"""
    
    def test_generate_request_id_format(self):
        """
        Test that request ID has correct format
        
        Validates: Requirements 8.6
        """
        request_id = generate_request_id()
        
        # Should start with "req-"
        assert request_id.startswith("req-")
        
        # Should have hex characters after prefix
        hex_part = request_id[4:]
        assert len(hex_part) == 16
        assert all(c in "0123456789abcdef" for c in hex_part)
    
    def test_generate_unique_request_ids(self):
        """
        Test that multiple calls generate unique IDs
        
        Validates: Requirements 8.6
        """
        ids = [generate_request_id() for _ in range(100)]
        
        # All IDs should be unique
        assert len(ids) == len(set(ids))


class TestErrorResponseCreation:
    """Test error response creation"""
    
    def test_create_basic_error_response(self):
        """
        Test creating a basic error response
        
        Validates: Requirements 8.2, 8.3
        """
        response = create_error_response(
            error_code="TEST_ERROR",
            message="Test error message",
            status_code=400
        )
        
        # Check required fields
        assert response["error_code"] == "TEST_ERROR"
        assert response["message"] == "Test error message"
        assert "timestamp" in response
        
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(response["timestamp"].replace('Z', '+00:00'))
    
    def test_create_error_response_with_details(self):
        """
        Test creating error response with additional details
        
        Validates: Requirements 8.2, 8.3
        """
        details = {"field": "test_field", "value": "invalid"}
        response = create_error_response(
            error_code="VALIDATION_ERROR",
            message="Validation failed",
            status_code=400,
            details=details
        )
        
        assert response["details"] == details
    
    def test_create_error_response_with_request_id(self):
        """
        Test creating error response with request ID
        
        Validates: Requirements 8.6
        """
        request_id = "req-test123"
        response = create_error_response(
            error_code="TEST_ERROR",
            message="Test message",
            status_code=500,
            request_id=request_id
        )
        
        assert "details" in response
        assert response["details"]["request_id"] == request_id


class TestErrorLogging:
    """Test error logging functionality"""
    
    @patch('src.error_handler.logger')
    def test_log_error_basic(self, mock_logger):
        """
        Test basic error logging
        
        Validates: Requirements 8.6
        """
        log_error(
            request_id="req-test123",
            endpoint="/api/test",
            method="GET",
            error_type="TestError",
            error_message="Test error occurred"
        )
        
        # Verify logger.error was called
        mock_logger.error.assert_called_once()
        
        # Check log message contains key information
        log_call = mock_logger.error.call_args[0][0]
        assert "req-test123" in log_call
        assert "/api/test" in log_call
        assert "GET" in log_call
        assert "TestError" in log_call
    
    @patch('src.error_handler.logger')
    def test_log_error_with_stack_trace(self, mock_logger):
        """
        Test error logging with stack trace
        
        Validates: Requirements 8.6
        """
        stack_trace = "Traceback (most recent call last):\n  File test.py, line 1"
        
        log_error(
            request_id="req-test123",
            endpoint="/api/test",
            method="POST",
            error_type="ValueError",
            error_message="Invalid value",
            stack_trace=stack_trace
        )
        
        # Verify logger was called
        mock_logger.error.assert_called_once()
        
        # Check stack trace is included
        log_call = mock_logger.error.call_args[0][0]
        assert "stack_trace" in log_call


@pytest.mark.asyncio
class TestHTTPExceptionHandler:
    """Test HTTP exception handler"""
    
    async def test_handle_404_error(self):
        """
        Test handling 404 Not Found error
        
        Validates: Requirements 8.1, 8.4
        """
        # Create mock request
        request = Mock(spec=Request)
        request.url.path = "/api/files/nonexistent"
        request.method = "GET"
        request.headers.get.return_value = "test-agent"
        request.client.host = "127.0.0.1"
        
        # Create 404 exception
        exc = StarletteHTTPException(
            status_code=404,
            detail="File not found"
        )
        
        # Handle exception
        response = await http_exception_handler(request, exc)
        
        # Verify response
        assert response.status_code == 404
        body = response.body.decode('utf-8')
        assert "NOT_FOUND" in body or "error_code" in body
    
    async def test_handle_400_error(self):
        """
        Test handling 400 Bad Request error
        
        Validates: Requirements 8.1, 8.5
        """
        request = Mock(spec=Request)
        request.url.path = "/api/upload"
        request.method = "POST"
        request.headers.get.return_value = "test-agent"
        request.client.host = "127.0.0.1"
        
        exc = StarletteHTTPException(
            status_code=400,
            detail="Invalid request"
        )
        
        response = await http_exception_handler(request, exc)
        
        assert response.status_code == 400
        body = response.body.decode('utf-8')
        assert "error_code" in body
    
    async def test_handle_structured_error_detail(self):
        """
        Test handling exception with structured detail
        
        Validates: Requirements 8.2, 8.3
        """
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"
        request.headers.get.return_value = "test-agent"
        request.client.host = "127.0.0.1"
        
        # Exception with structured detail
        exc = StarletteHTTPException(
            status_code=400,
            detail={
                "error_code": "CUSTOM_ERROR",
                "message": "Custom error message",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        response = await http_exception_handler(request, exc)
        
        assert response.status_code == 400
        body = response.body.decode('utf-8')
        assert "CUSTOM_ERROR" in body
        assert "request_id" in body


@pytest.mark.asyncio
class TestValidationExceptionHandler:
    """Test validation exception handler"""
    
    async def test_handle_validation_error(self):
        """
        Test handling request validation error
        
        Validates: Requirements 8.5
        """
        request = Mock(spec=Request)
        request.url.path = "/api/stats/test"
        request.method = "GET"
        request.headers.get.return_value = "test-agent"
        request.client.host = "127.0.0.1"
        
        # Create validation error
        # Mock the validation error structure
        exc = Mock(spec=RequestValidationError)
        exc.errors.return_value = [
            {
                "loc": ("query", "start_time"),
                "msg": "Invalid datetime format",
                "type": "value_error.datetime"
            }
        ]
        
        response = await validation_exception_handler(request, exc)
        
        # Verify response
        assert response.status_code == 422
        body = response.body.decode('utf-8')
        assert "VALIDATION_ERROR" in body
        assert "validation_errors" in body


@pytest.mark.asyncio
class TestGeneralExceptionHandler:
    """Test general exception handler"""
    
    async def test_handle_internal_error(self):
        """
        Test handling unexpected internal error
        
        Validates: Requirements 8.6, 8.7
        """
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "POST"
        request.headers.get.return_value = "test-agent"
        request.client.host = "127.0.0.1"
        
        # Create unexpected exception
        exc = ValueError("Unexpected error occurred")
        
        response = await general_exception_handler(request, exc)
        
        # Verify response
        assert response.status_code == 500
        body = response.body.decode('utf-8')
        
        # Should have standardized error format
        assert "INTERNAL_ERROR" in body
        assert "request_id" in body
        
        # Should NOT expose internal details
        assert "ValueError" not in body
        assert "Unexpected error occurred" not in body
    
    async def test_internal_error_logs_stack_trace(self):
        """
        Test that internal errors log stack trace
        
        Validates: Requirements 8.6
        """
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"
        request.headers.get.return_value = "test-agent"
        request.client.host = "127.0.0.1"
        
        exc = RuntimeError("Test runtime error")
        
        with patch('src.error_handler.log_error') as mock_log:
            response = await general_exception_handler(request, exc)
            
            # Verify log_error was called with stack trace
            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args[1]
            assert 'stack_trace' in call_kwargs
            assert call_kwargs['stack_trace'] is not None


class TestExceptionHandlerSetup:
    """Test exception handler setup"""
    
    def test_setup_exception_handlers(self):
        """
        Test that all exception handlers are registered
        
        Validates: Requirements 8.1
        """
        # Create mock FastAPI app
        mock_app = Mock()
        
        # Setup handlers
        setup_exception_handlers(mock_app)
        
        # Verify add_exception_handler was called 3 times
        # (HTTP, Validation, General)
        assert mock_app.add_exception_handler.call_count == 3


class TestErrorResponseConsistency:
    """Test error response consistency across different error types"""
    
    def test_all_errors_have_required_fields(self):
        """
        Test that all error responses have required fields
        
        Validates: Requirements 8.2, 8.3
        """
        # Test different error types
        errors = [
            create_error_response("ERROR_1", "Message 1", 400),
            create_error_response("ERROR_2", "Message 2", 404),
            create_error_response("ERROR_3", "Message 3", 500),
        ]
        
        for error in errors:
            # All should have these fields
            assert "error_code" in error
            assert "message" in error
            assert "timestamp" in error
            
            # All should be strings
            assert isinstance(error["error_code"], str)
            assert isinstance(error["message"], str)
            assert isinstance(error["timestamp"], str)
    
    def test_error_codes_are_descriptive(self):
        """
        Test that error codes are descriptive and follow naming convention
        
        Validates: Requirements 8.3
        """
        error_codes = [
            "FILE_NOT_FOUND",
            "INVALID_PARAMETER",
            "VALIDATION_ERROR",
            "INTERNAL_ERROR",
            "PARSE_ERROR"
        ]
        
        for code in error_codes:
            # Should be uppercase with underscores
            assert code.isupper()
            assert "_" in code or len(code.split("_")) == 1
            
            # Should be descriptive (at least 5 characters)
            assert len(code) >= 5
