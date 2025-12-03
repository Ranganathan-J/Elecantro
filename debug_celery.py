"""
Debug script to diagnose Celery issues
Run this to identify why tasks are not executing
"""

import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from celery import current_app
import redis

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'


def log(message, color=None):
    if color:
        print(f"{color}{message}{END}")
    else:
        print(message)


def check_settings():
    """Check Django settings"""
    print("\n" + "="*60)
    log("⚙️  Checking Django Settings", BLUE)
    print("="*60)
    
    try:
        log(f"\nCELERY_BROKER_URL: {settings.CELERY_BROKER_URL}", GREEN)
        log(f"CELERY_RESULT_BACKEND: {settings.CELERY_RESULT_BACKEND}", GREEN)
        log(f"CELERY_TASK_ALWAYS_EAGER: {settings.CELERY_TASK_ALWAYS_EAGER}", 
            RED if settings.CELERY_TASK_ALWAYS_EAGER else GREEN)
        
        if settings.CELERY_TASK_ALWAYS_EAGER:
            log("\n⚠️  WARNING: CELERY_TASK_ALWAYS_EAGER is True!", YELLOW)
            log("This means tasks run synchronously (no Celery worker needed)", YELLOW)
            log("Set to False in settings.py for real async processing", YELLOW)
            return False
        
        return True
    except Exception as e:
        log(f"❌ Error checking settings: {str(e)}", RED)
        return False


def check_redis():
    """Check Redis connection"""
    print("\n" + "="*60)
    log("🔴 Checking Redis Connection", BLUE)
    print("="*60)
    
    try:
        # Parse broker URL
        broker_url = settings.CELERY_BROKER_URL
        log(f"\nBroker URL: {broker_url}", GREEN)
        
        # Try to connect
        if 'redis://' in broker_url:
            # Extract host and port
            parts = broker_url.replace('redis://', '').split('/')
            host_port = parts[0].split(':')
            host = host_port[0] if host_port[0] else 'localhost'
            port = int(host_port[1]) if len(host_port) > 1 else 6379
            
            log(f"Connecting to Redis at {host}:{port}...", YELLOW)
            
            r = redis.Redis(host=host, port=port, db=0)
            r.ping()
            
            log("✅ Redis connection successful!", GREEN)
            
            # Check queue length
            queue_length = r.llen('celery')
            log(f"Tasks in queue: {queue_length}", GREEN)
            
            return True
        else:
            log("⚠️  Not using Redis broker", YELLOW)
            return True
            
    except redis.ConnectionError as e:
        log(f"❌ Redis connection failed: {str(e)}", RED)
        log("\nPossible solutions:", YELLOW)
        log("1. Start Redis: redis-server", YELLOW)
        log("2. Check Redis is running: redis-cli ping", YELLOW)
        log("3. Docker: docker-compose up redis", YELLOW)
        return False
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
        return False


def check_celery_app():
    """Check Celery app configuration"""
    print("\n" + "="*60)
    log("📋 Checking Celery App", BLUE)
    print("="*60)
    
    try:
        app = current_app
        
        log(f"\nCelery app name: {app.main}", GREEN)
        log(f"Broker: {app.conf.broker_url}", GREEN)
        log(f"Result backend: {app.conf.result_backend}", GREEN)
        
        # Check registered tasks
        registered_tasks = list(app.tasks.keys())
        log(f"\nRegistered tasks: {len(registered_tasks)}", GREEN)
        
        # Show our tasks
        our_tasks = [t for t in registered_tasks if 'data_ingestion' in t or 'analysis' in t]
        log(f"Our tasks: {len(our_tasks)}", GREEN)
        for task in our_tasks[:5]:
            log(f"  - {task}", GREEN)
        
        return True
        
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
        return False


def check_celery_worker():
    """Check if Celery worker is running"""
    print("\n" + "="*60)
    log("👷 Checking Celery Worker", BLUE)
    print("="*60)
    
    try:
        app = current_app
        
        # Try to inspect workers
        inspect = app.control.inspect(timeout=3)
        
        log("\nLooking for active workers...", YELLOW)
        active_workers = inspect.active()
        
        if active_workers:
            log(f"✅ Found {len(active_workers)} active worker(s)!", GREEN)
            for worker_name, tasks in active_workers.items():
                log(f"\n  Worker: {worker_name}", GREEN)
                log(f"  Active tasks: {len(tasks)}", GREEN)
            return True
        else:
            log("❌ No active workers found!", RED)
            log("\nPossible solutions:", YELLOW)
            log("1. Start worker: celery -A core worker -l info", YELLOW)
            log("2. Docker: docker-compose up celery_worker", YELLOW)
            log("3. Check worker logs for errors", YELLOW)
            return False
            
    except Exception as e:
        log(f"❌ Could not connect to workers: {str(e)}", RED)
        log("\nThis usually means NO WORKER IS RUNNING", YELLOW)
        log("\nStart a worker with:", YELLOW)
        log("  celery -A core worker -l info", YELLOW)
        log("or", YELLOW)
        log("  docker-compose up celery_worker", YELLOW)
        return False


def check_task_execution():
    """Try to execute a simple task"""
    print("\n" + "="*60)
    log("🧪 Testing Task Execution", BLUE)
    print("="*60)
    
    try:
        from data_ingestion.tasks import test_celery
        
        log("\nSubmitting test task...", YELLOW)
        result = test_celery.delay()
        log(f"Task ID: {result.id}", GREEN)
        
        log("Waiting 5 seconds for result...", YELLOW)
        try:
            response = result.get(timeout=5)
            log(f"✅ Task executed! Result: {response}", GREEN)
            return True
        except Exception as e:
            log(f"❌ Task timed out or failed: {str(e)}", RED)
            log("\nThis confirms the worker is not processing tasks", YELLOW)
            return False
            
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
        return False


def check_database():
    """Check database for feedback data"""
    print("\n" + "="*60)
    log("💾 Checking Database", BLUE)
    print("="*60)
    
    try:
        from data_ingestion.models import RawFeed
        from analysis.models import ProcessedFeedback
        from django.db.models import Count
        
        total_feedbacks = RawFeed.objects.count()
        log(f"\nTotal feedbacks: {total_feedbacks}", GREEN)
        
        if total_feedbacks > 0:
            status_counts = RawFeed.objects.values('status').annotate(
                count=Count('id')
            )
            log("\nStatus breakdown:", GREEN)
            for item in status_counts:
                log(f"  {item['status']}: {item['count']}", GREEN)
        
        processed_count = ProcessedFeedback.objects.count()
        log(f"\nProcessed feedbacks: {processed_count}", GREEN)
        
        if total_feedbacks > 0 and processed_count == 0:
            log("\n⚠️  Feedbacks exist but none are processed!", YELLOW)
            log("This confirms tasks are not being executed", YELLOW)
        
        return True
        
    except Exception as e:
        log(f"❌ Database error: {str(e)}", RED)
        return False


def main():
    """Run all checks"""
    print("\n" + "="*60)
    log("🔍 CELERY DIAGNOSTIC TOOL", BLUE)
    print("="*60)
    
    results = {
        'settings': check_settings(),
        'redis': check_redis(),
        'celery_app': check_celery_app(),
        'worker': check_celery_worker(),
        'task_execution': check_task_execution(),
        'database': check_database(),
    }
    
    # Summary
    print("\n" + "="*60)
    log("📋 Diagnostic Summary", BLUE)
    print("="*60)
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        color = GREEN if passed else RED
        log(f"{check_name.upper()}: {status}", color)
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print("\n" + "="*60)
    log(f"Results: {passed_count}/{total_count} checks passed", BLUE)
    print("="*60)
    
    # Recommendations
    if not results['redis']:
        print("\n🔴 CRITICAL: Redis is not running!")
        print("Start Redis with:")
        print("  redis-server")
        print("or")
        print("  docker-compose up -d redis")
    
    if not results['worker']:
        print("\n👷 CRITICAL: Celery worker is not running!")
        print("Start worker with:")
        print("  celery -A core worker -l info")
        print("or")
        print("  docker-compose up -d celery_worker")
    
    if results['settings'] and results['redis'] and results['worker']:
        print("\n✅ All critical components are working!")
        if not results['task_execution']:
            print("\n⚠️  But task execution failed - check worker logs:")
            print("  docker-compose logs celery_worker")
            print("or check the terminal where worker is running")
    
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n\n⚠️  Diagnostic interrupted by user", YELLOW)
    except Exception as e:
        log(f"\n\n❌ Diagnostic failed: {str(e)}", RED)
        import traceback
        traceback.print_exc()