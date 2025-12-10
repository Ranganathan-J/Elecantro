from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import time
import logging
import random

logger = logging.getLogger(__name__)


# ==================== DAY 5: TEST TASKS ====================

@shared_task
def test_celery():
    """Simple test task to verify Celery is working"""
    logger.info("✅ Celery test task executed successfully!")
    return "Celery is working!"


@shared_task
def print_random_feedback():
    """
    Periodic task that prints a random feedback every 10 seconds.
    This is for Day 5 testing.
    """
    from data_ingestion.models import RawFeed
    
    try:
        # Get random feedback
        feedback = RawFeed.objects.order_by('?').first()
        
        if feedback:
            preview = feedback.text[:100] + '...' if len(feedback.text) > 100 else feedback.text
            logger.info(f"""
            ==================== PERIODIC FEEDBACK ====================
            ID: {feedback.id}
            Entity: {feedback.entity.name}
            Source: {feedback.source}
            Text: {preview}
            Status: {feedback.status}
            ===========================================================
            """)
            return f"Printed feedback #{feedback.id}"
        else:
            logger.info("No feedbacks found in database")
            return "No feedbacks available"
            
    except Exception as e:
        logger.error(f"Error in print_random_feedback: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def add_numbers(a, b):
    """Simple math task for testing"""
    result = a + b
    logger.info(f"Addition: {a} + {b} = {result}")
    return result


@shared_task
def long_running_task(duration=10):
    """Task that takes some time to complete"""
    logger.info(f"Starting long task ({duration} seconds)...")
    time.sleep(duration)
    logger.info("Long task completed!")
    return f"Completed after {duration} seconds"


# ==================== DAY 6-7: FEEDBACK PROCESSING ====================

# REPLACE the process_feedback task in data_ingestion/tasks.py with this:

@shared_task(bind=True, max_retries=3)
def process_feedback_with_ai(self, feedback_id):
    """
    Process feedback with REAL AI models (Days 8-13).
    
    This replaces the placeholder version with actual HuggingFace models.
    
    Args:
        feedback_id: ID of the RawFeed to process
    """
    from data_ingestion.models import RawFeed
    from analysis.models import ProcessedFeedback
    from analysis.ai_processor import get_ai_processor
    
    start_time = time.time()
    
    try:
        # Get the raw feedback
        raw_feed = RawFeed.objects.select_for_update().get(id=feedback_id)
        
        logger.info(f"🤖 AI Processing feedback #{feedback_id}")
        
        # Update status
        raw_feed.status = 'processing'
        raw_feed.save(update_fields=['status'])
        
        # ==================== REAL AI PROCESSING ====================
        
        # Get AI processor (singleton, models loaded once)
        processor = get_ai_processor()
        
        # Run complete AI pipeline
        ai_results = processor.process_feedback_complete(raw_feed.text)
        
        # ==================== END AI PROCESSING ====================
        
        processing_time = time.time() - start_time
        
        # Create or update ProcessedFeedback record
        with transaction.atomic():
            processed, created = ProcessedFeedback.objects.update_or_create(
                raw_feed=raw_feed,
                defaults={
                    'sentiment': ai_results['sentiment'],
                    'sentiment_score': ai_results['sentiment_score'],
                    'topics': ai_results['topics'],
                    'embeddings': ai_results['embeddings'],
                    'summary': ai_results['summary'],
                    'key_phrases': ai_results['key_phrases'],
                    'urgency': ai_results.get('urgency', 'medium'),
                    'urgency_score': ai_results.get('urgency_score', 0.5),
                    'processing_time': processing_time,
                    'model_version': ai_results['model_version']
                }
            )
            
            # Update raw feed status
            raw_feed.status = 'processed'
            raw_feed.processed_at = timezone.now()
            raw_feed.save(update_fields=['status', 'processed_at'])
        
        logger.info(
            f"✅ AI Processed feedback #{feedback_id} in {processing_time:.2f}s "
            f"- Sentiment: {ai_results['sentiment']} ({ai_results['sentiment_score']:.2f}) "
            f"- Urgency: {ai_results.get('urgency', 'N/A')}"
        )
        
        return {
            'status': 'success',
            'feedback_id': feedback_id,
            'sentiment': ai_results['sentiment'],
            'sentiment_score': ai_results['sentiment_score'],
            'topics': ai_results['topics'],
            'urgency': ai_results.get('urgency'),
            'processing_time': processing_time
        }
        
    except RawFeed.DoesNotExist:
        logger.error(f"❌ RawFeed #{feedback_id} not found")
        return {'status': 'error', 'message': 'Feedback not found'}
        
    except Exception as e:
        logger.error(f"❌ Error AI processing feedback #{feedback_id}: {str(e)}")
        
        # Update status to failed
        try:
            raw_feed = RawFeed.objects.get(id=feedback_id)
            raw_feed.status = 'failed'
            raw_feed.error_message = str(e)
            raw_feed.save(update_fields=['status', 'error_message'])
        except:
            pass
        
        # Retry the task
        retry_delay = 60 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=retry_delay)


@shared_task
def process_bulk_feedbacks(feedback_ids):
    """
    Process multiple feedbacks in bulk.
    
    Args:
        feedback_ids: List of RawFeed IDs to process
    """
    logger.info(f"📦 Processing bulk upload: {len(feedback_ids)} feedbacks")
    
    results = {
        'total': len(feedback_ids),
        'queued': 0,
        'failed': 0,
        'task_ids': []
    }
    
    for feedback_id in feedback_ids:
        try:
            task = process_feedback_with_ai.delay(feedback_id)
            results['task_ids'].append({
                'feedback_id': feedback_id,
                'task_id': task.id
            })
            results['queued'] += 1
        except Exception as e:
            logger.error(f"Failed to queue feedback #{feedback_id}: {str(e)}")
            results['failed'] += 1
    
    logger.info(
        f"✅ Bulk processing queued: {results['queued']} success, "
        f"{results['failed']} failed"
    )
    
    return results


@shared_task
def process_pending_feedbacks():
    """
    Periodic task to process all pending (new) feedbacks.
    Runs every minute via Celery Beat.
    """
    from data_ingestion.models import RawFeed
    
    try:
        # Get all feedbacks with 'new' status
        pending = RawFeed.objects.filter(status='new')
        count = pending.count()
        
        if count == 0:
            logger.info("📭 No pending feedbacks to process")
            return {'status': 'success', 'processed': 0}
        
        logger.info(f"📬 Found {count} pending feedbacks")
        
        # Queue each for processing
        queued = 0
        for feedback in pending[:100]:  # Process max 100 at a time
            try:
                process_feedback_with_ai.delay(feedback.id)
                queued += 1
            except Exception as e:
                logger.error(f"Failed to queue feedback #{feedback.id}: {str(e)}")
        
        logger.info(f"✅ Queued {queued} feedbacks for processing")
        
        return {
            'status': 'success',
            'found': count,
            'queued': queued
        }
        
    except Exception as e:
        logger.error(f"❌ Error in process_pending_feedbacks: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def reprocess_failed_feedbacks():
    """
    Retry processing all failed feedbacks.
    Can be called manually or scheduled.
    """
    from data_ingestion.models import RawFeed
    
    try:
        failed = RawFeed.objects.filter(status='failed')
        count = failed.count()
        
        if count == 0:
            logger.info("No failed feedbacks to reprocess")
            return {'status': 'success', 'reprocessed': 0}
        
        logger.info(f"🔄 Reprocessing {count} failed feedbacks")
        
        # Reset status and queue for processing
        reprocessed = 0
        for feedback in failed:
            feedback.status = 'new'
            feedback.error_message = None
            feedback.save(update_fields=['status', 'error_message'])
            
            process_feedback_with_ai.delay(feedback.id)
            reprocessed += 1
        
        logger.info(f"✅ Queued {reprocessed} failed feedbacks for reprocessing")
        
        return {
            'status': 'success',
            'reprocessed': reprocessed
        }
        
    except Exception as e:
        logger.error(f"Error in reprocess_failed_feedbacks: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def cleanup_old_feedbacks():
    """
    Periodic task to clean up old processed feedbacks.
    Runs daily at 2 AM via Celery Beat.
    """
    from data_ingestion.models import RawFeed
    
    try:
        # Delete feedbacks older than 90 days
        cutoff_date = timezone.now() - timedelta(days=90)
        
        old_feedbacks = RawFeed.objects.filter(
            status='processed',
            processed_at__lt=cutoff_date
        )
        
        count = old_feedbacks.count()
        
        if count > 0:
            old_feedbacks.delete()
            logger.info(f"🗑️ Cleaned up {count} old feedbacks")
        else:
            logger.info("No old feedbacks to clean up")
        
        return {
            'status': 'success',
            'deleted_count': count
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_feedbacks: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def generate_daily_report():
    """
    Generate daily statistics report.
    Can be scheduled to run daily.
    """
    from data_ingestion.models import RawFeed, BusinessEntity
    from analysis.models import ProcessedFeedback
    from django.db.models import Count, Avg
    
    try:
        today = timezone.now().date()
        
        # Get today's statistics
        today_feedbacks = RawFeed.objects.filter(created_at__date=today)
        
        report = {
            'date': today.isoformat(),
            'total_feedbacks': today_feedbacks.count(),
            'by_status': dict(
                today_feedbacks.values('status').annotate(
                    count=Count('id')
                ).values_list('status', 'count')
            ),
            'by_source': dict(
                today_feedbacks.values('source').annotate(
                    count=Count('id')
                ).values_list('source', 'count')
            ),
            'average_rating': today_feedbacks.aggregate(
                avg=Avg('rating')
            )['avg'] or 0,
        }
        
        # Get sentiment breakdown
        today_processed = ProcessedFeedback.objects.filter(
            processed_at__date=today
        )
        
        report['sentiment_breakdown'] = dict(
            today_processed.values('sentiment').annotate(
                count=Count('id')
            ).values_list('sentiment', 'count')
        )
        
        logger.info(f"📊 Daily Report Generated: {report}")
        
        return {
            'status': 'success',
            'report': report
        }
        
    except Exception as e:
        logger.error(f"Error generating daily report: {str(e)}")
        return {'status': 'error', 'message': str(e)}
    




@shared_task
def generate_insights_task(entity_id=None, days_back=30):
    """
    Celery task to generate insights for entities.
    
    Args:
        entity_id: Optional entity ID. If None, generates for all entities.
        days_back: Number of days to analyze
    """
    from analysis.insights_generator import generate_insights_for_entity
    from data_ingestion.models import BusinessEntity
    
    try:
        if entity_id:
            # Generate for specific entity
            result = generate_insights_for_entity(entity_id, days_back)
            logger.info(f"Generated insights for entity {entity_id}: {result}")
            return result
        else:
            # Generate for all active entities
            entities = BusinessEntity.objects.filter(is_active=True)
            results = []
            
            for entity in entities:
                try:
                    result = generate_insights_for_entity(entity.id, days_back)
                    results.append(result)
                    logger.info(f"Generated insights for entity {entity.id}: {result}")
                except Exception as e:
                    logger.error(f"Failed to generate insights for entity {entity.id}: {str(e)}")
            
            total_generated = sum(r['total_generated'] for r in results)
            total_saved = sum(r['total_saved'] for r in results)
            
            logger.info(f"Total insights generated: {total_generated}, saved: {total_saved}")
            
            return {
                'entities_processed': len(results),
                'total_generated': total_generated,
                'total_saved': total_saved,
                'results': results
            }
    
    except Exception as e:
        logger.error(f"Insight generation task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def daily_insights_generation():
    """
    Periodic task to generate daily insights for all entities.
    Run daily via Celery Beat.
    """
    logger.info("Starting daily insights generation")
    return generate_insights_task.delay(entity_id=None, days_back=30)


@shared_task
def cleanup_old_insights():
    """
    Periodic task to deactivate old resolved insights.
    Run weekly via Celery Beat.
    """
    from analysis.models import Insight
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        # Deactivate resolved insights older than 90 days
        cutoff_date = timezone.now() - timedelta(days=90)
        
        old_insights = Insight.objects.filter(
            is_resolved=True,
            resolved_at__lt=cutoff_date,
            is_active=True
        )
        
        count = old_insights.count()
        
        if count > 0:
            old_insights.update(is_active=False)
            logger.info(f"Deactivated {count} old resolved insights")
        else:
            logger.info("No old insights to clean up")
        
        return {
            'status': 'success',
            'deactivated_count': count
        }
        
    except Exception as e:
        logger.error(f"Insight cleanup failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}









process_feedback = process_feedback_with_ai