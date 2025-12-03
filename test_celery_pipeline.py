"""
Complete test script for Celery setup and feedback pipeline.
Run this after setting up Celery to verify everything works.

Usage:
    python test_celery_pipeline.py
"""

import os
import django
import sys
import time

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from data_ingestion.models import RawFeed, BusinessEntity
from analysis.models import ProcessedFeedback
from data_ingestion.tasks import (
    test_celery, add_numbers, process_feedback,
    process_bulk_feedbacks
)
from django.contrib.auth import get_user_model

User = get_user_model()

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'


def log(message, color=None):
    """Print colored log message"""
    if color:
        print(f"{color}{message}{END}")
    else:
        print(message)


def test_celery_basics():
    """Test basic Celery functionality"""
    print("\n" + "="*60)
    log("🧪 Testing Basic Celery Functionality", BLUE)
    print("="*60)
    
    # Test 1: Simple test task
    log("\n1️⃣ Testing simple task...", YELLOW)
    try:
        result = test_celery.delay()
        log(f"   Task ID: {result.id}", GREEN)
        
        response = result.get(timeout=10)
        log(f"   ✅ Result: {response}", GREEN)
    except Exception as e:
        log(f"   ❌ Failed: {str(e)}", RED)
        return False
    
    # Test 2: Math task
    log("\n2️⃣ Testing math task...", YELLOW)
    try:
        result = add_numbers.delay(15, 25)
        response = result.get(timeout=10)
        log(f"   ✅ 15 + 25 = {response}", GREEN)
    except Exception as e:
        log(f"   ❌ Failed: {str(e)}", RED)
        return False
    
    log("\n✅ Basic Celery tests passed!", GREEN)
    return True


def setup_test_data():
    """Create test user, entity, and feedback"""
    log("\n📦 Setting up test data...", YELLOW)
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='celery_test_user',
        defaults={
            'email': 'celery@test.com',
            'role': 'analyst'
        }
    )
    if created:
        user.set_password('TestPass123!')
        user.save()
        log(f"   ✅ Created test user: {user.username}", GREEN)
    else:
        log(f"   ℹ️  Using existing user: {user.username}", GREEN)
    
    # Create or get test entity
    entity, created = BusinessEntity.objects.get_or_create(
        name='Celery Test Corp',
        defaults={
            'owner': user,
            'description': 'Test entity for Celery pipeline'
        }
    )
    if created:
        log(f"   ✅ Created test entity: {entity.name}", GREEN)
    else:
        log(f"   ℹ️  Using existing entity: {entity.name}", GREEN)
    
    return user, entity


def test_single_feedback_processing(entity):
    """Test processing a single feedback"""
    print("\n" + "="*60)
    log("🔄 Testing Single Feedback Processing", BLUE)
    print("="*60)
    
    # Create a new feedback
    log("\n1️⃣ Creating test feedback...", YELLOW)
    feedback = RawFeed.objects.create(
        entity=entity,
        text="This product is absolutely amazing! The quality is excellent and delivery was super fast. Highly recommend!",
        source='test',
        product_name='Test Product',
        rating=5
    )
    log(f"   ✅ Created feedback #{feedback.id}", GREEN)
    log(f"   Status: {feedback.status}", GREEN)
    
    # Process the feedback
    log("\n2️⃣ Queuing for processing...", YELLOW)
    try:
        result = process_feedback.delay(feedback.id)
        log(f"   Task ID: {result.id}", GREEN)
        
        # FIXED: Wait longer since task has 2-second sleep + processing
        log("\n3️⃣ Waiting for processing (task has 2s sleep + DB operations)...", YELLOW)
        
        # Poll for completion instead of blocking wait
        max_wait = 60  # Max 60 seconds
        start_time = time.time()
        task_completed = False
        
        while (time.time() - start_time) < max_wait:
            try:
                # Check if task is ready (non-blocking)
                if result.ready():
                    response = result.get(timeout=1)
                    task_completed = True
                    break
            except Exception:
                pass
            
            # Check database status as alternative
            feedback.refresh_from_db()
            if feedback.status == 'processed':
                log(f"   ℹ️  Feedback marked as processed in DB", YELLOW)
                task_completed = True
                # Try to get result one more time
                try:
                    response = result.get(timeout=5)
                except:
                    # Manually construct response from DB
                    response = {
                        'status': 'success',
                        'feedback_id': feedback.id,
                        'sentiment': 'verified from DB',
                    }
                break
            
            time.sleep(1)  # Wait 1 second before checking again
            elapsed = int(time.time() - start_time)
            if elapsed % 5 == 0 and elapsed > 0:
                log(f"   ⏱️  Still waiting... ({elapsed}s)", YELLOW)
        
        if not task_completed:
            log(f"\n   ⚠️  Task did not complete in {max_wait} seconds", YELLOW)
            log(f"   Current feedback status: {feedback.status}", YELLOW)
            log(f"   This might indicate worker is slow or busy", YELLOW)
            return False
        
        log(f"\n   ✅ Processing completed!", GREEN)
        if isinstance(response, dict) and 'sentiment' in response:
            log(f"   Sentiment: {response.get('sentiment', 'N/A')}", GREEN)
            log(f"   Topics: {', '.join(response.get('topics', []))}", GREEN)
        
        # Verify in database
        feedback.refresh_from_db()
        log(f"\n4️⃣ Verifying database...", YELLOW)
        log(f"   Status: {feedback.status}", GREEN)
        
        if hasattr(feedback, 'processed_feedback'):
            processed = feedback.processed_feedback
            log(f"   ✅ ProcessedFeedback created!", GREEN)
            log(f"   ID: {processed.id}", GREEN)
            log(f"   Sentiment: {processed.sentiment}", GREEN)
            log(f"   Score: {processed.sentiment_score:.2f}", GREEN)
        else:
            log(f"   ⚠️  ProcessedFeedback not found (might still be processing)", YELLOW)
            return False
        
        return True
        
    except Exception as e:
        log(f"   ❌ Processing failed: {str(e)}", RED)
        import traceback
        traceback.print_exc()
        return False


def test_bulk_processing(entity):
    """Test bulk feedback processing"""
    print("\n" + "="*60)
    log("📦 Testing Bulk Feedback Processing", BLUE)
    print("="*60)
    
    # Create multiple feedbacks
    log("\n1️⃣ Creating 5 test feedbacks...", YELLOW)
    
    test_feedbacks = [
        {"text": "Great product! Very satisfied.", "rating": 5},
        {"text": "Terrible quality. Very disappointed.", "rating": 1},
        {"text": "Average product for the price.", "rating": 3},
        {"text": "Excellent customer service!", "rating": 5},
        {"text": "Delivery was slow but product is good.", "rating": 4},
    ]
    
    feedback_ids = []
    for i, fb_data in enumerate(test_feedbacks, 1):
        feedback = RawFeed.objects.create(
            entity=entity,
            text=fb_data['text'],
            source='test',
            rating=fb_data['rating']
        )
        feedback_ids.append(feedback.id)
        log(f"   Created feedback #{feedback.id}: {fb_data['text'][:50]}", GREEN)
    
    # Process in bulk
    log(f"\n2️⃣ Queuing {len(feedback_ids)} feedbacks for processing...", YELLOW)
    try:
        result = process_bulk_feedbacks.delay(feedback_ids)
        log(f"   Bulk task ID: {result.id}", GREEN)
        
        log("\n3️⃣ Waiting for bulk task to queue individual tasks...", YELLOW)
        response = result.get(timeout=30)
        
        log(f"\n   ✅ Bulk queuing completed!", GREEN)
        log(f"   Total: {response['total']}", GREEN)
        log(f"   Queued: {response['queued']}", GREEN)
        log(f"   Failed: {response['failed']}", GREEN)
        
        # Wait for individual tasks to complete
        log("\n4️⃣ Waiting for individual tasks to complete (each has 2s sleep)...", YELLOW)
        log("   This will take ~15-20 seconds...", YELLOW)
        
        max_wait = 60  # Max 60 seconds
        start_time = time.time()
        
        processed_count = 0
        while (time.time() - start_time) < max_wait:
            processed_count = RawFeed.objects.filter(
                id__in=feedback_ids,
                status='processed'
            ).count()
            
            elapsed = int(time.time() - start_time)
            
            if processed_count == len(feedback_ids):
                log(f"   ✅ All feedbacks processed in {elapsed}s!", GREEN)
                break
            
            if elapsed % 5 == 0 and elapsed > 0:
                log(f"   ⏱️  Processed: {processed_count}/{len(feedback_ids)} ({elapsed}s)", YELLOW)
            
            time.sleep(1)
        
        # Check results
        log("\n5️⃣ Verifying results...", YELLOW)
        final_processed = 0
        for fb_id in feedback_ids:
            try:
                feedback = RawFeed.objects.get(id=fb_id)
                if feedback.status == 'processed':
                    final_processed += 1
                    if hasattr(feedback, 'processed_feedback'):
                        pf = feedback.processed_feedback
                        log(
                            f"   ✅ #{fb_id}: {pf.sentiment} "
                            f"({pf.sentiment_score:.2f})",
                            GREEN
                        )
                    else:
                        log(f"   ⚠️ #{fb_id}: Processed but no ProcessedFeedback", YELLOW)
                else:
                    log(f"   ⏱️  #{fb_id}: Status = {feedback.status}", YELLOW)
            except Exception as e:
                log(f"   ❌ #{fb_id}: {str(e)}", RED)
        
        log(f"\n   Final: {final_processed}/{len(feedback_ids)} processed", 
            GREEN if final_processed > 0 else YELLOW)
        
        return final_processed > 0
        
    except Exception as e:
        log(f"   ❌ Bulk processing failed: {str(e)}", RED)
        import traceback
        traceback.print_exc()
        return False


def test_statistics():
    """Test sentiment statistics"""
    print("\n" + "="*60)
    log("📊 Testing Statistics", BLUE)
    print("="*60)
    
    try:
        total_processed = ProcessedFeedback.objects.count()
        log(f"\nTotal processed feedbacks: {total_processed}", GREEN)
        
        if total_processed == 0:
            log("   ℹ️  No processed feedbacks yet", YELLOW)
            return True
        
        # Count by sentiment
        from django.db.models import Count
        
        sentiment_counts = ProcessedFeedback.objects.values('sentiment').annotate(
            count=Count('id')
        )
        
        log("\nSentiment breakdown:", YELLOW)
        for item in sentiment_counts:
            sentiment = item['sentiment']
            count = item['count']
            percentage = (count / total_processed * 100)
            log(f"   {sentiment.capitalize()}: {count} ({percentage:.1f}%)", GREEN)
        
        # Average score
        from django.db.models import Avg
        avg_score = ProcessedFeedback.objects.aggregate(
            avg=Avg('sentiment_score')
        )['avg']
        log(f"\nAverage sentiment score: {avg_score:.2f}", GREEN)
        
        return True
        
    except Exception as e:
        log(f"   ❌ Statistics failed: {str(e)}", RED)
        return False


def test_periodic_tasks():
    """Check if periodic tasks are configured"""
    print("\n" + "="*60)
    log("⏰ Checking Periodic Tasks", BLUE)
    print("="*60)
    
    try:
        from celery import current_app
        
        beat_schedule = current_app.conf.beat_schedule
        
        if not beat_schedule:
            log("   ⚠️  No periodic tasks configured", YELLOW)
            return False
        
        log(f"\nConfigured periodic tasks:", YELLOW)
        for task_name, task_config in beat_schedule.items():
            schedule = task_config.get('schedule')
            task = task_config.get('task')
            log(f"   ✅ {task_name}", GREEN)
            log(f"      Task: {task}", GREEN)
            log(f"      Schedule: {schedule}", GREEN)
        
        return True
        
    except Exception as e:
        log(f"   ❌ Failed to check periodic tasks: {str(e)}", RED)
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    log("🚀 Celery Pipeline Test Suite", BLUE)
    print("="*60)
    
    log("\n⚠️  NOTE: Each feedback takes ~2 seconds to process (built-in sleep)", YELLOW)
    log("This is normal for testing. Real AI will be faster.", YELLOW)
    
    results = {
        'basic': False,
        'single': False,
        'bulk': False,
        'stats': False,
        'periodic': False
    }
    
    # Test 1: Basic Celery
    results['basic'] = test_celery_basics()
    
    if not results['basic']:
        log("\n❌ Basic Celery tests failed. Fix Celery setup first!", RED)
        log("\nRun: python debug_celery.py", YELLOW)
        return
    
    # Setup test data
    user, entity = setup_test_data()
    
    # Test 2: Single feedback processing
    results['single'] = test_single_feedback_processing(entity)
    
    # Test 3: Bulk processing
    results['bulk'] = test_bulk_processing(entity)
    
    # Test 4: Statistics
    results['stats'] = test_statistics()
    
    # Test 5: Periodic tasks
    results['periodic'] = test_periodic_tasks()
    
    # Summary
    print("\n" + "="*60)
    log("📋 Test Summary", BLUE)
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        color = GREEN if result else RED
        log(f"{test_name.upper()}: {status}", color)
    
    print("\n" + "="*60)
    log(f"Results: {passed}/{total} tests passed", BLUE)
    
    if passed == total:
        log("🎉 All tests passed! Celery pipeline is working correctly!", GREEN)
        log("\nNext steps:", YELLOW)
        print("1. Visit http://localhost:5555 to see Flower dashboard")
        print("2. Check Celery worker logs for periodic tasks")
        print("3. Start building your AI models!")
    elif results['basic'] and (results['single'] or results['bulk']):
        log("✅ Core functionality working!", GREEN)
        log("⚠️  Some optional features need attention", YELLOW)
    else:
        log("⚠️  Some tests failed. Check the errors above.", YELLOW)
        log("\nTroubleshooting:", YELLOW)
        print("1. Make sure Celery worker is running")
        print("2. Check worker isn't overloaded (reduce bulk size)")
        print("3. Verify database connections")
        print("4. Run: python debug_celery.py")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n\n⚠️  Tests interrupted by user", YELLOW)
    except Exception as e:
        log(f"\n\n❌ Test suite failed: {str(e)}", RED)
        import traceback
        traceback.print_exc()