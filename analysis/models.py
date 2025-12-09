from django.db import models
from data_ingestion.models import RawFeed, BusinessEntity


class ProcessedFeedback(models.Model):
    """
    AI-processed feedback with complete analysis.
    Updated for Days 8-13 with real AI models.
    """
    
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]
    
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Link to original raw feedback
    raw_feed = models.OneToOneField(
        RawFeed,
        on_delete=models.CASCADE,
        related_name='processed_feedback',
        help_text="Original raw feedback"
    )
    
    # Sentiment Analysis (Day 8)
    sentiment = models.CharField(
        max_length=20,
        choices=SENTIMENT_CHOICES,
        help_text="Overall sentiment"
    )
    sentiment_score = models.FloatField(
        help_text="Confidence score for sentiment (0.0 to 1.0)"
    )
    
    # Topic Extraction (Day 9)
    topics = models.JSONField(
        default=list,
        help_text="Extracted topics/keywords"
    )
    
    # Embeddings (Day 11)
    embeddings = models.JSONField(
        default=list,
        help_text="Vector embeddings (384-dimensional)"
    )
    
    # Summarization (Day 10)
    summary = models.TextField(
        blank=True,
        null=True,
        help_text="AI-generated summary"
    )
    
    # Key phrases
    key_phrases = models.JSONField(
        default=list,
        help_text="Important phrases extracted"
    )
    
    # Urgency Classification (Bonus)
    urgency = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        default='medium',
        help_text="Urgency level"
    )
    urgency_score = models.FloatField(
        default=0.5,
        help_text="Urgency confidence score (0.0 to 1.0)"
    )
    
    # Processing Metadata
    processing_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Time taken to process (seconds)"
    )
    model_version = models.CharField(
        max_length=50,
        default="v1.0",
        help_text="Version of AI models used"
    )
    processed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When processed"
    )
    
    class Meta:
        ordering = ['-processed_at']
        indexes = [
            models.Index(fields=['sentiment', 'processed_at']),
            models.Index(fields=['urgency', 'processed_at']),
            models.Index(fields=['sentiment_score']),
        ]
        verbose_name = "Processed Feedback"
        verbose_name_plural = "Processed Feedbacks"
    
    def __str__(self):
        return f"Processed #{self.raw_feed.id} - {self.sentiment} | {self.urgency}"
    
    @property
    def is_positive(self):
        return self.sentiment == 'positive'
    
    @property
    def is_negative(self):
        return self.sentiment == 'negative'
    
    @property
    def is_urgent(self):
        return self.urgency in ['high', 'critical']
    
    @property
    def embedding_dimension(self):
        return len(self.embeddings) if self.embeddings else 0


class Insight(models.Model):
    """
    Actionable insights generated from processed feedback.
    Days 15-16: Insights Generation
    """
    
    TYPE_CHOICES = [
        ('recurring_complaint', 'Recurring Complaint'),
        ('recurring_praise', 'Recurring Praise'),
        ('critical_feedback', 'Critical Feedback'),
        ('product_issue', 'Product Issue'),
        ('product_success', 'Product Success'),
        ('sentiment_trend', 'Sentiment Trend'),
        ('urgent_action', 'Urgent Action'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Relationships
    entity = models.ForeignKey(
        BusinessEntity,
        on_delete=models.CASCADE,
        related_name='insights',
        help_text="Entity this insight belongs to"
    )
    
    # Insight Details
    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        help_text="Type of insight"
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium',
        help_text="Severity/priority level"
    )
    title = models.CharField(
        max_length=255,
        help_text="Insight title"
    )
    description = models.TextField(
        help_text="Detailed description of the insight"
    )
    recommendation = models.TextField(
        help_text="Actionable recommendations"
    )
    
    # Metrics
    metrics = models.JSONField(
        default=dict,
        help_text="Quantitative metrics supporting the insight"
    )
    
    # Related Data
    related_topics = models.JSONField(
        default=list,
        help_text="Related topics/keywords"
    )
    product_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Related product (if applicable)"
    )
    sample_feedbacks = models.JSONField(
        default=list,
        blank=True,
        help_text="Sample feedback examples"
    )
    
    # Status Tracking
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this insight is still relevant"
    )
    is_resolved = models.BooleanField(
        default=False,
        help_text="Whether this insight has been addressed"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When insight was resolved"
    )
    resolved_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes on how insight was resolved"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When insight was generated"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update time"
    )
    
    class Meta:
        ordering = ['-created_at', '-severity']
        indexes = [
            models.Index(fields=['entity', 'type', 'is_active']),
            models.Index(fields=['severity', 'is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_resolved', 'severity']),
        ]
        verbose_name = "Insight"
        verbose_name_plural = "Insights"
    
    def __str__(self):
        return f"{self.get_severity_display()}: {self.title}"
    
    @property
    def is_critical(self):
        return self.severity == 'critical'
    
    @property
    def is_high_priority(self):
        return self.severity in ['high', 'critical']
    
    @property
    def days_since_created(self):
        from django.utils import timezone
        return (timezone.now() - self.created_at).days
    
    def mark_resolved(self, notes=None):
        """Mark insight as resolved"""
        from django.utils import timezone
        self.is_resolved = True
        self.resolved_at = timezone.now()
        if notes:
            self.resolved_notes = notes
        self.save()