"""
Celery monitoring and logging configuration.
"""

import logging
from celery.signals import task_prerun, task_postrun, task_failure, task_success, task_retry
import time
import traceback

# Set up loggers
logger = logging.getLogger('celery')
task_logger = logging.getLogger('celery.task')
performance_logger = logging.getLogger('performance')


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """Log task start with performance tracking."""
    task._start_time = time.time()
    
    logger.info(
        f'Task started: {task.name} [{task_id}]',
        extra={
            'task_id': task_id,
            'task_name': task.name,
            'args_count': len(args) if args else 0,
            'kwargs_count': len(kwargs) if kwargs else 0,
            'event': 'task_started'
        }
    )
    
    task_logger.debug(
        f'Task {task.name} [{task_id}] started with args: {args}, kwargs: {kwargs}',
        extra={
            'task_id': task_id,
            'task_name': task.name,
            'args': args,
            'kwargs': kwargs,
            'event': 'task_started_debug'
        }
    )


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, retval=None, **extra):
    """Log task completion with performance metrics."""
    if hasattr(task, '_start_time'):
        duration = time.time() - task._start_time
    else:
        duration = 0
    
    logger.info(
        f'Task completed: {task.name} [{task_id}] in {duration:.3f}s',
        extra={
            'task_id': task_id,
            'task_name': task.name,
            'duration': duration,
            'return_value': str(retval)[:200] if retval else None,
            'event': 'task_completed'
        }
    )
    
    # Log performance data
    performance_logger.info(
        f'Task performance: {task.name}',
        extra={
            'task_name': task.name,
            'task_id': task_id,
            'duration': duration,
            'event_type': 'task_performance'
        }
    )


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """Log successful task completion."""
    task_id = kwargs.get('task_id', 'unknown')
    logger.info(
        f'Task succeeded: {sender.name} [{task_id}]',
        extra={
            'task_id': task_id,
            'task_name': sender.name,
            'result': str(result)[:200] if result else None,
            'event': 'task_success'
        }
    )


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback_info=None, **extra):
    """Log task failure with detailed error information."""
    error_details = {
        'task_id': task_id,
        'task_name': sender.name,
        'error_type': type(exception).__name__,
        'error_message': str(exception),
        'traceback': traceback.format_exc() if traceback_info else str(exception),
        'event': 'task_failed'
    }
    
    logger.error(
        f'Task failed: {sender.name} [{task_id}] - {exception}',
        extra=error_details,
        exc_info=True
    )
    
    task_logger.error(
        f'Task {sender.name} [{task_id}] failed with exception: {exception}',
        extra=error_details,
        exc_info=True
    )


@task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, traceback_info=None, **extra):
    """Log task retry attempts."""
    logger.warning(
        f'Task retry: {sender.name} [{task_id}] - Reason: {reason}',
        extra={
            'task_id': task_id,
            'task_name': sender.name,
            'retry_reason': str(reason),
            'traceback': traceback.format_exc() if traceback_info else None,
            'event': 'task_retry'
        }
    )


# Custom task monitoring decorator
def monitor_task(task_func):
    """
    Decorator to add additional monitoring to specific tasks.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        task_name = task_func.__name__
        
        try:
            result = task_func(*args, **kwargs)
            duration = time.time() - start_time
            
            performance_logger.info(
                f'Custom task completed: {task_name}',
                extra={
                    'task_name': task_name,
                    'duration': duration,
                    'success': True,
                    'event_type': 'custom_task_performance'
                }
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            performance_logger.error(
                f'Custom task failed: {task_name}',
                extra={
                    'task_name': task_name,
                    'duration': duration,
                    'success': False,
                    'error': str(e),
                    'event_type': 'custom_task_performance'
                }
            )
            
            raise e
    
    return wrapper


# Health check for Celery workers
def check_celery_health():
    """
    Check if Celery workers are running and responsive.
    """
    try:
        from celery import current_app
        inspect = current_app.control.inspect(timeout=5.0)
        stats = inspect.stats()
        active = inspect.active()
        
        if stats is None:
            return {
                'status': 'unhealthy',
                'reason': 'No workers responding'
            }
        
        worker_count = len(stats)
        active_tasks = sum(len(tasks) for tasks in (active or {}).values())
        
        return {
            'status': 'healthy',
            'worker_count': worker_count,
            'active_tasks': active_tasks,
            'workers': list(stats.keys())
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'reason': str(e)
        }


# Task performance metrics
def get_task_metrics():
    """
    Get performance metrics for tasks.
    """
    try:
        from celery import current_app
        inspect = current_app.control.inspect(timeout=5.0)
        
        # Get various statistics
        stats = inspect.stats()
        active = inspect.active()
        scheduled = inspect.scheduled()
        reserved = inspect.reserved()
        
        metrics = {
            'total_workers': len(stats) if stats else 0,
            'active_tasks': sum(len(tasks) for tasks in (active or {}).values()),
            'scheduled_tasks': sum(len(tasks) for tasks in (scheduled or {}).values()),
            'reserved_tasks': sum(len(tasks) for tasks in (reserved or {}).values()),
            'workers': {}
        }
        
        # Add individual worker stats
        if stats:
            for worker_name, worker_stats in stats.items():
                metrics['workers'][worker_name] = {
                    'pool': worker_stats.get('pool', {}),
                    'total_tasks': worker_stats.get('total', 0),
                    'broker': worker_stats.get('broker', {})
                }
        
        return metrics
        
    except Exception as e:
        return {
            'error': str(e),
            'status': 'failed_to_get_metrics'
        }
