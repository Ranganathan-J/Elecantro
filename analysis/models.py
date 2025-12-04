from django.db import models
from data_ingestion.models import RawFeed


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