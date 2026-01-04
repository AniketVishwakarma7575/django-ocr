# ocr/utils/exception_handler.py

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('ocr')


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework
    
    Args:
        exc: The exception raised
        context: Context information about the exception
    
    Returns:
        Response: Custom error response
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If response is None, it means we have an unhandled exception
    if response is None:
        logger.error(
            f"Unhandled exception: {str(exc)}",
            exc_info=True
        )
        
        return Response(
            {
                'error': 'Internal server error',
                'details': str(exc)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Customize the response format
    if hasattr(response, 'data'):
        custom_response_data = {
            'error': 'Request failed',
        }
        
        # Handle different types of error responses
        if isinstance(response.data, dict):
            # If there's a detail field, use it as the main error message
            if 'detail' in response.data:
                custom_response_data['error'] = str(response.data['detail'])
            else:
                custom_response_data['details'] = response.data
        elif isinstance(response.data, list):
            custom_response_data['details'] = response.data
        else:
            custom_response_data['error'] = str(response.data)
        
        response.data = custom_response_data
    
    # Log the exception
    logger.warning(
        f"API exception: {exc.__class__.__name__} - {str(exc)}",
        extra={
            'status_code': response.status_code,
            'path': context.get('request').path if context.get('request') else None
        }
    )
    
    return response