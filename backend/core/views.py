"""
Health check and monitoring views for the application.
"""

import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
import redis
import time
import psutil
import os

logger = logging.getLogger('django')
performance_logger = logging.getLogger('performance')

@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(View):
    """
    Comprehensive health check endpoint for load balancers and monitoring.
    GET /health/
    """
    
    def get(self, request):
        start_time = time.time()
        checks = {
            'database': self._check_database(),
            'cache': self._check_cache(),
            'redis': self._check_redis(),
            'disk_space': self._check_disk_space(),
            'memory': self._check_memory(),
        }
        
        # Add Celery health check if available
        try:
            from .celery_monitoring import check_celery_health
            checks['celery'] = check_celery_health()
        except ImportError:
            checks['celery'] = {'status': 'not_configured'}
        
        all_healthy = all(
            check.get('status') == 'healthy' 
            for check in checks.values() 
            if isinstance(check, dict) and 'status' in check
        )
        
        status_code = 200 if all_healthy else 503
        duration = time.time() - start_time
        
        response_data = {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'timestamp': time.time(),
            'duration': f'{duration:.3f}s',
            'checks': checks,
            'version': getattr(settings, 'APP_VERSION', '1.0.0'),
            'environment': getattr(settings, 'ENVIRONMENT', 'development')
        }
        
        # Log health check performance
        performance_logger.info(
            f'Health check completed in {duration:.3f}s',
            extra={
                'event_type': 'health_check',
                'duration': duration,
                'status': response_data['status'],
                'checks_count': len(checks)
            }
        )
        
        return JsonResponse(response_data, status=status_code)
    
    def _check_database(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return {'status': 'healthy', 'message': 'Database connection successful'}
        except Exception as e:
            logger.error(f'Database health check failed: {e}')
            return {'status': 'unhealthy', 'error': str(e)}
    
    def _check_cache(self):
        try:
            cache.set('health_check', 'ok', 10)
            result = cache.get('health_check')
            if result == 'ok':
                return {'status': 'healthy', 'message': 'Cache connection successful'}
            else:
                return {'status': 'unhealthy', 'error': 'Cache read/write failed'}
        except Exception as e:
            logger.error(f'Cache health check failed: {e}')
            return {'status': 'unhealthy', 'error': str(e)}
    
    def _check_redis(self):
        try:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://redis:6379/0')
            r = redis.from_url(redis_url)
            r.ping()
            return {'status': 'healthy', 'message': 'Redis connection successful'}
        except Exception as e:
            logger.error(f'Redis health check failed: {e}')
            return {'status': 'unhealthy', 'error': str(e)}
    
    def _check_disk_space(self):
        try:
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100
            
            if free_percent < 10:
                return {'status': 'unhealthy', 'error': f'Low disk space: {free_percent:.1f}% free'}
            elif free_percent < 20:
                return {'status': 'warning', 'message': f'Low disk space: {free_percent:.1f}% free'}
            else:
                return {'status': 'healthy', 'message': f'Disk space OK: {free_percent:.1f}% free'}
        except Exception as e:
            logger.error(f'Disk space check failed: {e}')
            return {'status': 'unhealthy', 'error': str(e)}
    
    def _check_memory(self):
        try:
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                return {'status': 'unhealthy', 'error': f'High memory usage: {memory.percent:.1f}%'}
            elif memory.percent > 80:
                return {'status': 'warning', 'message': f'High memory usage: {memory.percent:.1f}%'}
            else:
                return {'status': 'healthy', 'message': f'Memory usage OK: {memory.percent:.1f}%'}
        except Exception as e:
            logger.error(f'Memory check failed: {e}')
            return {'status': 'unhealthy', 'error': str(e)}


class MetricsView(View):
    """
    Application metrics endpoint for monitoring.
    GET /metrics/
    """
    
    def get(self, request):
        try:
            metrics = {
                'application': self._get_application_metrics(),
                'system': self._get_system_metrics(),
                'database': self._get_database_metrics(),
                'cache': self._get_cache_metrics(),
                'users': self._get_user_metrics(),
            }
            
            # Add Celery metrics if available
            try:
                from .celery_monitoring import get_task_metrics
                metrics['celery'] = get_task_metrics()
            except ImportError:
                metrics['celery'] = {'status': 'not_configured'}
            
            return JsonResponse(metrics)
            
        except Exception as e:
            logger.error(f'Metrics endpoint failed: {e}')
            return JsonResponse(
                {'error': 'Failed to collect metrics', 'details': str(e)},
                status=500
            )
    
    def _get_application_metrics(self):
        return {
            'version': getattr(settings, 'APP_VERSION', '1.0.0'),
            'environment': getattr(settings, 'ENVIRONMENT', 'development'),
            'debug_mode': settings.DEBUG,
            'uptime': time.time() - psutil.boot_time(),
            'process_id': os.getpid(),
        }
    
    def _get_system_metrics(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100,
                    'used': disk.used,
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_database_metrics(self):
        try:
            with connection.cursor() as cursor:
                # Get database size (PostgreSQL specific)
                cursor.execute("""
                    SELECT 
                        pg_size_pretty(pg_database_size(current_database())) as size,
                        (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public') as table_count
                """)
                result = cursor.fetchone()
                
                return {
                    'size': result[0] if result else 'unknown',
                    'table_count': result[1] if result else 0,
                    'status': 'connected'
                }
        except Exception as e:
            return {'error': str(e), 'status': 'disconnected'}
    
    def _get_cache_metrics(self):
        try:
            cache.set('metrics_test', 'ok', 60)
            result = cache.get('metrics_test')
            
            return {
                'status': 'connected' if result == 'ok' else 'disconnected',
                'test_result': result
            }
        except Exception as e:
            return {'error': str(e), 'status': 'disconnected'}
    
    def _get_user_metrics(self):
        try:
            return {
                'total_users': User.objects.count(),
                'active_users': User.objects.filter(is_active=True).count(),
                'admin_users': User.objects.filter(is_staff=True).count(),
            }
        except Exception as e:
            return {'error': str(e)}


@method_decorator(csrf_exempt, name='dispatch')
class LogView(View):
    """
    View recent application logs.
    GET /logs/?level=INFO&limit=100
    """
    
    def get(self, request):
        level = request.GET.get('level', 'INFO')
        limit = int(request.GET.get('limit', 100))
        
        try:
            log_file = settings.LOGS_DIR / 'django.log'
            
            if not log_file.exists():
                return JsonResponse({'error': 'Log file not found'}, status=404)
            
            # Read last N lines from log file
            lines = self._tail_file(log_file, limit)
            
            # Filter by log level if specified
            if level != 'ALL':
                lines = [line for line in lines if level in line]
            
            return JsonResponse({
                'logs': lines[-limit:],  # Return only the requested number of lines
                'level': level,
                'limit': limit,
                'total_lines': len(lines)
            })
            
        except Exception as e:
            logger.error(f'Log view failed: {e}')
            return JsonResponse(
                {'error': 'Failed to read logs', 'details': str(e)},
                status=500
            )
    
    def _tail_file(self, file_path, num_lines):
        """Read last N lines from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return [line.strip() for line in lines[-num_lines:]]
        except Exception as e:
            logger.error(f'Failed to read log file {file_path}: {e}')
            return []
