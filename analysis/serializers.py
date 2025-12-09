from rest_framework import serializers
from .models import ProcessedFeedback, Insight
from data_ingestion.serializer import RawFeedSerializer


class ProcessedFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for ProcessedFeedback with related raw feed data"""
    
    # Include raw feed details
    raw_feed_text = serializers.CharField(source='raw_feed.text', read_only=True)
    entity_name = serializers.CharField(source='raw_feed.entity.name', read_only=True)
    product_name = serializers.CharField(source='raw_feed.product_name', read_only=True)
    rating = serializers.IntegerField(source='raw_feed.rating', read_only=True)
    source = serializers.CharField(source='raw_feed.source', read_only=True)
    sentiment_display = serializers.CharField(source='get_sentiment_display', read_only=True)
    
    class Meta:
        model = ProcessedFeedback
        fields = [
            'id', 'raw_feed', 'raw_feed_text', 'entity_name',
            'product_name', 'rating', 'source',
            'sentiment', 'sentiment_display', 'sentiment_score',
            'topics', 'key_phrases', 'summary',
            'urgency', 'urgency_score',
            'processing_time', 'model_version', 'processed_at'
        ]
        read_only_fields = ['processed_at']


class ProcessedFeedbackListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    
    entity_name = serializers.CharField(source='raw_feed.entity.name', read_only=True)
    text_preview = serializers.SerializerMethodField()
    sentiment_display = serializers.CharField(source='get_sentiment_display', read_only=True)
    
    class Meta:
        model = ProcessedFeedback
        fields = [
            'id', 'raw_feed', 'entity_name', 'text_preview',
            'sentiment', 'sentiment_display', 'sentiment_score',
            'topics', 'urgency', 'processed_at'
        ]
    
    def get_text_preview(self, obj):
        text = obj.raw_feed.text
        return text[:80] + '...' if len(text) > 80 else text


class SentimentStatsSerializer(serializers.Serializer):
    """Serializer for sentiment statistics"""
    
    total_processed = serializers.IntegerField()
    positive_count = serializers.IntegerField()
    neutral_count = serializers.IntegerField()
    negative_count = serializers.IntegerField()
    positive_percentage = serializers.FloatField()
    neutral_percentage = serializers.FloatField()
    negative_percentage = serializers.FloatField()
    average_sentiment_score = serializers.FloatField()
    topic_breakdown = serializers.DictField()


class InsightSerializer(serializers.ModelSerializer):
    """Full serializer for Insight"""
    
    entity_name = serializers.CharField(source='entity.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    days_since_created = serializers.IntegerField(read_only=True)
    is_critical = serializers.BooleanField(read_only=True)
    is_high_priority = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Insight
        fields = [
            'id', 'entity', 'entity_name', 'type', 'type_display',
            'severity', 'severity_display', 'title', 'description',
            'recommendation', 'metrics', 'related_topics',
            'product_name', 'sample_feedbacks', 'is_active',
            'is_resolved', 'resolved_at', 'resolved_notes',
            'created_at', 'updated_at', 'days_since_created',
            'is_critical', 'is_high_priority'
        ]
        read_only_fields = ['created_at', 'updated_at']


class InsightListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for insight lists"""
    
    entity_name = serializers.CharField(source='entity.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = Insight
        fields = [
            'id', 'entity_name', 'type', 'type_display',
            'severity', 'severity_display', 'title',
            'is_active', 'is_resolved', 'created_at'
        ]


class InsightResolveSerializer(serializers.Serializer):
    """Serializer for resolving insights"""
    
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Notes on how the insight was resolved"
    )


class AnalyticsSerializer(serializers.Serializer):
    """Serializer for dashboard analytics"""
    
    # Sentiment Overview
    total_feedbacks = serializers.IntegerField()
    sentiment_breakdown = serializers.DictField()
    average_sentiment = serializers.FloatField()
    
    # Trends
    sentiment_trend = serializers.ListField()
    volume_trend = serializers.ListField()
    
    # Topics
    top_topics = serializers.ListField()
    top_complaints = serializers.ListField()
    top_praise = serializers.ListField()
    
    # Products
    product_performance = serializers.ListField()
    
    # Urgency
    urgency_breakdown = serializers.DictField()
    
    # Insights
    active_insights_count = serializers.IntegerField()
    critical_insights_count = serializers.IntegerField()
    
    # Time periods
    period_days = serializers.IntegerField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()


class TopicAnalyticsSerializer(serializers.Serializer):
    """Serializer for topic-specific analytics"""
    
    topic = serializers.CharField()
    total_mentions = serializers.IntegerField()
    sentiment_breakdown = serializers.DictField()
    average_rating = serializers.FloatField()
    trend_data = serializers.ListField()
    related_products = serializers.ListField()
    sample_feedbacks = serializers.ListField()


class ProductAnalyticsSerializer(serializers.Serializer):
    """Serializer for product-specific analytics"""
    
    product_name = serializers.CharField()
    total_feedbacks = serializers.IntegerField()
    sentiment_breakdown = serializers.DictField()
    average_rating = serializers.FloatField()
    average_sentiment_score = serializers.FloatField()
    top_topics = serializers.ListField()
    top_complaints = serializers.ListField()
    top_praise = serializers.ListField()
    trend_data = serializers.ListField()