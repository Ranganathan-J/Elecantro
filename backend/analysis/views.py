from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from collections import Counter, defaultdict
import csv
from django.http import HttpResponse

from .models import ProcessedFeedback, Insight
from .serializers import (
    ProcessedFeedbackSerializer,
    ProcessedFeedbackListSerializer,
    SentimentStatsSerializer,
    InsightSerializer,
    InsightListSerializer,
    InsightResolveSerializer,
    AnalyticsSerializer,
    TopicAnalyticsSerializer,
    ProductAnalyticsSerializer
)
from .insights_generator import generate_insights_for_entity
from data_ingestion.tasks import reprocess_failed_feedbacks
import logging

logger = logging.getLogger(__name__)


class ProcessedFeedbackViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing processed feedbacks.
    
    list: GET /api/analysis/processed-feedbacks/
    retrieve: GET /api/analysis/processed-feedbacks/{id}/
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['raw_feed__text', 'summary', 'topics']
    ordering_fields = ['processed_at', 'sentiment_score', 'urgency']
    ordering = ['-processed_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProcessedFeedbackListSerializer
        return ProcessedFeedbackSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Base queryset with optimized joins
        queryset = ProcessedFeedback.objects.select_related(
            'raw_feed',
            'raw_feed__entity',
            'raw_feed__entity__owner'
        )
        
        # Filter by user permissions
        if not user.is_admin:
            queryset = queryset.filter(raw_feed__entity__owner=user)
        
        # Apply filters
        return self._apply_filters(queryset)
    
    def _apply_filters(self, queryset):
        """Apply query parameter filters"""
        
        # Filter by entity
        entity_id = self.request.query_params.get('entity_id')
        if entity_id:
            queryset = queryset.filter(raw_feed__entity_id=entity_id)
        
        # Filter by sentiment
        sentiment = self.request.query_params.get('sentiment')
        if sentiment:
            queryset = queryset.filter(sentiment=sentiment)
        
        # Filter by urgency
        urgency = self.request.query_params.get('urgency')
        if urgency:
            queryset = queryset.filter(urgency=urgency)
        
        # Filter by minimum sentiment score
        min_score = self.request.query_params.get('min_score')
        if min_score:
            queryset = queryset.filter(sentiment_score__gte=float(min_score))
        
        # Filter by topic
        topic = self.request.query_params.get('topic')
        if topic:
            queryset = queryset.filter(topics__contains=[topic])
        
        # Filter by product
        product = self.request.query_params.get('product')
        if product:
            queryset = queryset.filter(raw_feed__product_name__icontains=product)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(processed_at__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(processed_at__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def sentiment_stats(self, request):
        """
        Get sentiment statistics.
        
        GET /api/analysis/processed-feedbacks/sentiment_stats/
        """
        queryset = self.get_queryset()
        
        total = queryset.count()
        
        if total == 0:
            return Response({
                'total_processed': 0,
                'message': 'No processed feedbacks found'
            })
        
        # Count by sentiment
        sentiment_counts = queryset.values('sentiment').annotate(
            count=Count('id')
        )
        
        positive_count = next(
            (item['count'] for item in sentiment_counts if item['sentiment'] == 'positive'),
            0
        )
        neutral_count = next(
            (item['count'] for item in sentiment_counts if item['sentiment'] == 'neutral'),
            0
        )
        negative_count = next(
            (item['count'] for item in sentiment_counts if item['sentiment'] == 'negative'),
            0
        )
        
        # Calculate percentages
        stats = {
            'total_processed': total,
            'positive_count': positive_count,
            'neutral_count': neutral_count,
            'negative_count': negative_count,
            'positive_percentage': (positive_count / total * 100) if total > 0 else 0,
            'neutral_percentage': (neutral_count / total * 100) if total > 0 else 0,
            'negative_percentage': (negative_count / total * 100) if total > 0 else 0,
            'average_sentiment_score': queryset.aggregate(
                avg=Avg('sentiment_score')
            )['avg'] or 0,
            'topic_breakdown': self._get_topic_breakdown(queryset)
        }
        
        serializer = SentimentStatsSerializer(stats)
        return Response(serializer.data)
    
    def _get_topic_breakdown(self, queryset):
        """Get breakdown of topics from processed feedbacks"""
        topic_counts = {}
        
        for feedback in queryset:
            for topic in feedback.topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Sort by count and return top 10
        sorted_topics = sorted(
            topic_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return dict(sorted_topics)
    
    @action(detail=False, methods=['post'])
    def reprocess_failed(self, request):
        """Trigger reprocessing of all failed feedbacks"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can trigger reprocessing'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task = reprocess_failed_feedbacks.delay()
        
        logger.info(f"Reprocess task triggered by {request.user.username}")
        
        return Response({
            'message': 'Reprocessing task triggered',
            'task_id': task.id
        })
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        Export processed feedbacks to CSV.
        
        GET /api/analysis/processed-feedbacks/export_csv/
        """
        queryset = self.get_queryset()
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="feedbacks_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'ID', 'Entity', 'Text', 'Product', 'Source', 'Rating',
            'Sentiment', 'Sentiment Score', 'Topics', 'Urgency',
            'Key Phrases', 'Summary', 'Processed At'
        ])
        
        # Write data
        for feedback in queryset:
            writer.writerow([
                feedback.id,
                feedback.raw_feed.entity.name,
                feedback.raw_feed.text,
                feedback.raw_feed.product_name or '',
                feedback.raw_feed.source,
                feedback.raw_feed.rating or '',
                feedback.sentiment,
                f"{feedback.sentiment_score:.2f}",
                ', '.join(feedback.topics),
                feedback.urgency,
                ', '.join(feedback.key_phrases),
                feedback.summary or '',
                feedback.processed_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        logger.info(f"CSV export by {request.user.username}: {queryset.count()} rows")
        
        return response


class InsightViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing insights.
    
    list: GET /api/analysis/insights/
    retrieve: GET /api/analysis/insights/{id}/
    create: POST /api/analysis/insights/
    update: PUT /api/analysis/insights/{id}/
    destroy: DELETE /api/analysis/insights/{id}/
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'related_topics']
    ordering_fields = ['created_at', 'severity', 'type']
    ordering = ['-severity', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InsightListSerializer
        return InsightSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Base queryset
        queryset = Insight.objects.select_related('entity')
        
        # Filter by user permissions
        if not user.is_admin:
            queryset = queryset.filter(entity__owner=user)
        
        # Apply filters
        return self._apply_filters(queryset)
    
    def _apply_filters(self, queryset):
        """Apply query parameter filters"""
        
        # Filter by entity
        entity_id = self.request.query_params.get('entity_id')
        if entity_id:
            queryset = queryset.filter(entity_id=entity_id)
        
        # Filter by type
        insight_type = self.request.query_params.get('type')
        if insight_type:
            queryset = queryset.filter(type=insight_type)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by resolved status
        is_resolved = self.request.query_params.get('is_resolved')
        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved.lower() == 'true')
        
        # Filter by product
        product = self.request.query_params.get('product')
        if product:
            queryset = queryset.filter(product_name__icontains=product)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Mark insight as resolved.
        
        POST /api/analysis/insights/{id}/resolve/
        """
        insight = self.get_object()
        
        serializer = InsightResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notes = serializer.validated_data.get('notes', '')
        insight.mark_resolved(notes=notes)
        
        logger.info(f"Insight #{insight.id} resolved by {request.user.username}")
        
        return Response({
            'message': 'Insight marked as resolved',
            'insight': InsightSerializer(insight).data
        })
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """
        Reactivate a resolved insight.
        
        POST /api/analysis/insights/{id}/reactivate/
        """
        insight = self.get_object()
        
        insight.is_resolved = False
        insight.resolved_at = None
        insight.resolved_notes = None
        insight.save()
        
        logger.info(f"Insight #{insight.id} reactivated by {request.user.username}")
        
        return Response({
            'message': 'Insight reactivated',
            'insight': InsightSerializer(insight).data
        })
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate insights for an entity.
        
        POST /api/analysis/insights/generate/
        Body: {
            "entity_id": 1,
            "days_back": 30
        }
        """
        entity_id = request.data.get('entity_id')
        days_back = int(request.data.get('days_back', 30))
        
        if not entity_id:
            return Response(
                {'error': 'entity_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        from data_ingestion.models import BusinessEntity
        try:
            entity = BusinessEntity.objects.get(id=entity_id)
            if not request.user.is_admin and entity.owner != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except BusinessEntity.DoesNotExist:
            return Response(
                {'error': 'Entity not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate insights
        try:
            result = generate_insights_for_entity(entity_id, days_back)
            
            logger.info(f"Insights generated by {request.user.username}: {result}")
            
            return Response({
                'message': 'Insights generated successfully',
                **result
            })
        except Exception as e:
            logger.error(f"Insight generation failed: {str(e)}")
            return Response(
                {'error': f'Failed to generate insights: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get insight summary statistics.
        
        GET /api/analysis/insights/summary/
        """
        queryset = self.get_queryset()
        
        total = queryset.count()
        
        if total == 0:
            return Response({
                'total': 0,
                'message': 'No insights found'
            })
        
        # Count by severity
        by_severity = dict(
            queryset.values('severity').annotate(
                count=Count('id')
            ).values_list('severity', 'count')
        )
        
        # Count by type
        by_type = dict(
            queryset.values('type').annotate(
                count=Count('id')
            ).values_list('type', 'count')
        )
        
        # Active vs resolved
        active_count = queryset.filter(is_active=True, is_resolved=False).count()
        resolved_count = queryset.filter(is_resolved=True).count()
        
        return Response({
            'total': total,
            'active': active_count,
            'resolved': resolved_count,
            'by_severity': by_severity,
            'by_type': by_type
        })


class DashboardAnalyticsView(APIView):
    """
    Comprehensive dashboard analytics.
    
    GET /api/analysis/dashboard/
    Query params:
    - entity_id: Filter by entity
    - days: Number of days to analyze (default 30)
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses=AnalyticsSerializer,
        summary="Dashboard analytics"
    )
    def get(self, request):
        entity_id = request.query_params.get('entity_id')
        days = int(request.query_params.get('days', 30))
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get queryset
        queryset = ProcessedFeedback.objects.select_related(
            'raw_feed', 'raw_feed__entity'
        ).filter(processed_at__gte=cutoff_date)
        
        # Filter by entity
        if entity_id:
            queryset = queryset.filter(raw_feed__entity_id=entity_id)
        
        # Filter by user permissions
        if not request.user.is_admin:
            queryset = queryset.filter(raw_feed__entity__owner=request.user)
        
        if queryset.count() == 0:
            return Response({
                'message': 'No data available for the selected period',
                'total_feedbacks': 0
            })
        
        # Build analytics
        analytics = {
            'total_feedbacks': queryset.count(),
            'sentiment_breakdown': self._get_sentiment_breakdown(queryset),
            'average_sentiment': queryset.aggregate(avg=Avg('sentiment_score'))['avg'] or 0,
            'sentiment_trend': self._get_sentiment_trend(queryset, days),
            'volume_trend': self._get_volume_trend(queryset, days),
            'top_topics': self._get_top_topics(queryset),
            'top_complaints': self._get_top_complaints(queryset),
            'top_praise': self._get_top_praise(queryset),
            'product_performance': self._get_product_performance(queryset),
            'urgency_breakdown': self._get_urgency_breakdown(queryset),
            'active_insights_count': self._get_active_insights_count(entity_id),
            'critical_insights_count': self._get_critical_insights_count(entity_id),
            'period_days': days,
            'start_date': cutoff_date,
            'end_date': timezone.now()
        }
        
        serializer = AnalyticsSerializer(analytics)
        return Response(serializer.data)
    
    def _get_sentiment_breakdown(self, queryset):
        """Get sentiment distribution"""
        total = queryset.count()
        sentiments = queryset.values('sentiment').annotate(count=Count('id'))
        
        result = {s['sentiment']: {
            'count': s['count'],
            'percentage': (s['count'] / total * 100) if total > 0 else 0
        } for s in sentiments}
        
        return result
    
    def _get_sentiment_trend(self, queryset, days):
        """Get sentiment trend over time"""
        trend = []
        
        for i in range(days - 1, -1, -1):
            date = timezone.now() - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_feedbacks = queryset.filter(
                processed_at__gte=day_start,
                processed_at__lt=day_end
            )
            
            if day_feedbacks.count() > 0:
                avg_score = day_feedbacks.aggregate(avg=Avg('sentiment_score'))['avg']
                
                trend.append({
                    'date': date.date().isoformat(),
                    'average_sentiment': round(avg_score, 3),
                    'count': day_feedbacks.count(),
                    'positive': day_feedbacks.filter(sentiment='positive').count(),
                    'neutral': day_feedbacks.filter(sentiment='neutral').count(),
                    'negative': day_feedbacks.filter(sentiment='negative').count()
                })
        
        return trend
    
    def _get_volume_trend(self, queryset, days):
        """Get feedback volume trend"""
        trend = []
        
        for i in range(days - 1, -1, -1):
            date = timezone.now() - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            count = queryset.filter(
                processed_at__gte=day_start,
                processed_at__lt=day_end
            ).count()
            
            trend.append({
                'date': date.date().isoformat(),
                'count': count
            })
        
        return trend
    
    def _get_top_topics(self, queryset):
        """Get most mentioned topics"""
        topic_counter = Counter()
        
        for feedback in queryset:
            for topic in feedback.topics:
                topic_counter[topic] += 1
        
        return [
            {'topic': topic, 'count': count}
            for topic, count in topic_counter.most_common(10)
        ]
    
    def _get_top_complaints(self, queryset):
        """Get most common complaint topics"""
        topic_counter = Counter()
        
        negative_feedbacks = queryset.filter(sentiment='negative')
        
        for feedback in negative_feedbacks:
            for topic in feedback.topics:
                topic_counter[topic] += 1
        
        return [
            {'topic': topic, 'count': count}
            for topic, count in topic_counter.most_common(10)
        ]
    
    def _get_top_praise(self, queryset):
        """Get most common praise topics"""
        topic_counter = Counter()
        
        positive_feedbacks = queryset.filter(sentiment='positive')
        
        for feedback in positive_feedbacks:
            for topic in feedback.topics:
                topic_counter[topic] += 1
        
        return [
            {'topic': topic, 'count': count}
            for topic, count in topic_counter.most_common(10)
        ]
    
    def _get_product_performance(self, queryset):
        """Get product performance metrics"""
        products = queryset.filter(
            raw_feed__product_name__isnull=False
        ).exclude(
            raw_feed__product_name=''
        ).values('raw_feed__product_name').annotate(
            total=Count('id'),
            avg_sentiment=Avg('sentiment_score'),
            avg_rating=Avg('raw_feed__rating'),
            negative_count=Count('id', filter=Q(sentiment='negative'))
        ).order_by('-total')[:10]
        
        result = []
        for product in products:
            negative_pct = (product['negative_count'] / product['total']) * 100 if product['total'] > 0 else 0
            
            result.append({
                'product': product['raw_feed__product_name'],
                'total_feedbacks': product['total'],
                'avg_sentiment_score': round(product['avg_sentiment'], 2),
                'avg_rating': round(product['avg_rating'], 2) if product['avg_rating'] else None,
                'negative_percentage': round(negative_pct, 2)
            })
        
        return result
    
    def _get_urgency_breakdown(self, queryset):
        """Get urgency distribution"""
        total = queryset.count()
        urgencies = queryset.values('urgency').annotate(count=Count('id'))
        
        result = {u['urgency']: {
            'count': u['count'],
            'percentage': (u['count'] / total * 100) if total > 0 else 0
        } for u in urgencies}
        
        return result
    
    def _get_active_insights_count(self, entity_id):
        """Get count of active insights"""
        queryset = Insight.objects.filter(is_active=True, is_resolved=False)
        if entity_id:
            queryset = queryset.filter(entity_id=entity_id)
        return queryset.count()
    
    def _get_critical_insights_count(self, entity_id):
        """Get count of critical insights"""
        queryset = Insight.objects.filter(
            severity__in=['high', 'critical'],
            is_active=True,
            is_resolved=False
        )
        if entity_id:
            queryset = queryset.filter(entity_id=entity_id)
        return queryset.count()


class TopicAnalyticsView(APIView):
    """
    Topic-specific analytics.
    
    GET /api/analysis/topics/{topic}/
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses=TopicAnalyticsSerializer,
        summary="Topic analytics"
    )
    def get(self, request, topic):
        entity_id = request.query_params.get('entity_id')
        days = int(request.query_params.get('days', 30))
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get feedbacks containing this topic
        queryset = ProcessedFeedback.objects.filter(
            topics__contains=[topic],
            processed_at__gte=cutoff_date
        )
        
        # Filter by entity and permissions
        if entity_id:
            queryset = queryset.filter(raw_feed__entity_id=entity_id)
        
        if not request.user.is_admin:
            queryset = queryset.filter(raw_feed__entity__owner=request.user)
        
        if queryset.count() == 0:
            return Response({
                'message': f'No data found for topic: {topic}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Build analytics
        analytics = {
            'topic': topic,
            'total_mentions': queryset.count(),
            'sentiment_breakdown': self._get_sentiment_breakdown(queryset),
            'average_rating': self._get_average_rating(queryset),
            'trend_data': self._get_trend_data(queryset, days),
            'related_products': self._get_related_products(queryset),
            'sample_feedbacks': self._get_sample_feedbacks(queryset)
        }
        
        serializer = TopicAnalyticsSerializer(analytics)
        return Response(serializer.data)
    
    def _get_sentiment_breakdown(self, queryset):
        total = queryset.count()
        sentiments = queryset.values('sentiment').annotate(count=Count('id'))
        
        return {s['sentiment']: {
            'count': s['count'],
            'percentage': (s['count'] / total * 100) if total > 0 else 0
        } for s in sentiments}
    
    def _get_average_rating(self, queryset):
        avg = queryset.aggregate(avg=Avg('raw_feed__rating'))['avg']
        return round(avg, 2) if avg else None
    
    def _get_trend_data(self, queryset, days):
        trend = []
        
        for i in range(days - 1, -1, -1):
            date = timezone.now() - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            count = queryset.filter(
                processed_at__gte=day_start,
                processed_at__lt=day_end
            ).count()
            
            if count > 0:
                trend.append({
                    'date': date.date().isoformat(),
                    'count': count
                })
        
        return trend
    
    def _get_related_products(self, queryset):
        products = queryset.filter(
            raw_feed__product_name__isnull=False
        ).values('raw_feed__product_name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return [
            {'product': p['raw_feed__product_name'], 'count': p['count']}
            for p in products
        ]
    
    def _get_sample_feedbacks(self, queryset):
        samples = queryset.order_by('-processed_at')[:5]
        
        return [
            {
                'id': fb.raw_feed.id,
                'text': fb.raw_feed.text[:150],
                'sentiment': fb.sentiment,
                'rating': fb.raw_feed.rating
            }
            for fb in samples
        ]


class ProductAnalyticsView(APIView):
    """
    Product-specific analytics.
    
    GET /api/analysis/products/{product_name}/
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses=ProductAnalyticsSerializer,
        summary="Product analytics"
    )
    def get(self, request, product_name):
        entity_id = request.query_params.get('entity_id')
        days = int(request.query_params.get('days', 30))
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get feedbacks for this product
        queryset = ProcessedFeedback.objects.filter(
            raw_feed__product_name__iexact=product_name,
            processed_at__gte=cutoff_date
        )
        
        # Filter by entity and permissions
        if entity_id:
            queryset = queryset.filter(raw_feed__entity_id=entity_id)
        
        if not request.user.is_admin:
            queryset = queryset.filter(raw_feed__entity__owner=request.user)
        
        if queryset.count() == 0:
            return Response({
                'message': f'No data found for product: {product_name}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Build analytics
        analytics = {
            'product_name': product_name,
            'total_feedbacks': queryset.count(),
            'sentiment_breakdown': self._get_sentiment_breakdown(queryset),
            'average_rating': self._get_average_rating(queryset),
            'average_sentiment_score': self._get_average_sentiment(queryset),
            'top_topics': self._get_top_topics(queryset),
            'top_complaints': self._get_top_complaints(queryset),
            'top_praise': self._get_top_praise(queryset),
            'trend_data': self._get_trend_data(queryset, days)
        }
        
        serializer = ProductAnalyticsSerializer(analytics)
        return Response(serializer.data)
    
    def _get_sentiment_breakdown(self, queryset):
        total = queryset.count()
        sentiments = queryset.values('sentiment').annotate(count=Count('id'))
        
        return {s['sentiment']: {
            'count': s['count'],
            'percentage': (s['count'] / total * 100) if total > 0 else 0
        } for s in sentiments}
    
    def _get_average_rating(self, queryset):
        avg = queryset.aggregate(avg=Avg('raw_feed__rating'))['avg']
        return round(avg, 2) if avg else None
    
    def _get_average_sentiment(self, queryset):
        avg = queryset.aggregate(avg=Avg('sentiment_score'))['avg']
        return round(avg, 3) if avg else None


    # In _get_top_topics and similar methods
    def _get_top_topics(self, queryset, top_n=5):
        try:
            topic_counter = Counter()
            for feedback in queryset:
                for topic in feedback.topics:
                    topic_counter[topic] += 1
            return topic_counter.most_common(top_n)
        except Exception as e:
            logger.error(f"Error getting top topics: {str(e)}")
            return []  # Return empty list instead of crashing