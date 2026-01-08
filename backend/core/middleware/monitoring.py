import time
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

perf_logger = logging.getLogger('performance')
security_logger = logging.getLogger('security')


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Monitor request performance and log slow queries.
    """
    
    def process_request(self, request):
        request._start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log slow requests (>1 second)
            if duration > 1.0:
                perf_logger.warning(
                    f'Slow request: {request.method} {request.path} took {duration:.3f}s',
                    extra={
                        'path': request.path,
                        'method': request.method,
                        'duration': duration,
                        'status_code': response.status_code,
                        'user': getattr(request.user, 'username', 'anonymous')
                    }
                )
            
            # Log all requests in JSON format for analysis
            perf_logger.info(
                f'Request: {request.method} {request.path}',
                extra={
                    'path': request.path,
                    'method': request.method,
                    'duration': duration,
                    'status_code': response.status_code,
                    'user': getattr(request.user, 'username', 'anonymous'),
                    'ip_address': self.get_client_ip(request)
                }
            )
            
            # Add duration header
            response['X-Request-Duration'] = f'{duration:.3f}s'
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Log security-related events and suspicious activities.
    """
    
    def process_request(self, request):
        # Log authentication attempts
        if '/api/auth/' in request.path or '/api/token/' in request.path:
            security_logger.info(
                f'Auth attempt: {request.method} {request.path}',
                extra={
                    'path': request.path,
                    'method': request.method,
                    'ip_address': self.get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'user': getattr(request.user, 'username', 'anonymous')
                }
            )
    
    def process_response(self, request, response):
        # Log failed authentication attempts
        if response.status_code == 401 and ('/api/auth/' in request.path or '/api/token/' in request.path):
            security_logger.warning(
                f'Failed authentication: {request.method} {request.path}',
                extra={
                    'path': request.path,
                    'method': request.method,
                    'ip_address': self.get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'status_code': response.status_code
                }
            )
        
        # Log admin access attempts
        if '/admin/' in request.path or '/api/users/' in request.path:
            security_logger.info(
                f'Admin access: {request.method} {request.path}',
                extra={
                    'path': request.path,
                    'method': request.method,
                    'ip_address': self.get_client_ip(request),
                    'user': getattr(request.user, 'username', 'anonymous'),
                    'status_code': response.status_code
                }
            )
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Comprehensive request logging for debugging and monitoring.
    """
    
    def process_request(self, request):
        request._start_time = time.time()
        
        # Log request details
        logger = logging.getLogger('requests')
        logger.info(
            f'Incoming request: {request.method} {request.path}',
            extra={
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.GET),
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'content_type': request.content_type,
                'content_length': request.META.get('CONTENT_LENGTH', 0)
            }
        )
    
    def process_response(self, request, response):
        logger = logging.getLogger('requests')
        
        # Log response details
        logger.info(
            f'Outgoing response: {request.method} {request.path} -> {response.status_code}',
            extra={
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'response_size': len(response.content) if hasattr(response, 'content') else 0,
                'duration': time.time() - getattr(request, '_start_time', 0)
            }
        )
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
