"""
Insights Generation Module (Days 15-16)
Analyzes processed feedback to generate actionable insights.
"""

import logging
from typing import Dict, List, Any
from collections import Counter, defaultdict
from datetime import timedelta
from django.db.models import Count, Avg, Q
from django.utils import timezone
from .models import ProcessedFeedback, Insight

logger = logging.getLogger(__name__)


class InsightsGenerator:
    """
    Generate actionable insights from processed feedback.
    """
    
    def __init__(self, entity_id=None, days_back=30):
        """
        Initialize insights generator.
        
        Args:
            entity_id: Optional entity ID to filter by
            days_back: Number of days to analyze (default 30)
        """
        self.entity_id = entity_id
        self.days_back = days_back
        self.cutoff_date = timezone.now() - timedelta(days=days_back)
    
    def get_queryset(self):
        """Get filtered queryset of processed feedbacks"""
        queryset = ProcessedFeedback.objects.select_related(
            'raw_feed', 'raw_feed__entity'
        ).filter(processed_at__gte=self.cutoff_date)
        
        if self.entity_id:
            queryset = queryset.filter(raw_feed__entity_id=self.entity_id)
        
        return queryset
    
    def generate_all_insights(self) -> List[Dict[str, Any]]:
        """
        Generate all types of insights.
        
        Returns:
            List of insight dictionaries
        """
        logger.info(f"Generating insights for entity={self.entity_id}, days={self.days_back}")
        
        insights = []
        
        # 1. Detect recurring complaints
        insights.extend(self.detect_recurring_complaints())
        
        # 2. Detect recurring praise
        insights.extend(self.detect_recurring_praise())
        
        # 3. Identify critical negative feedback
        insights.extend(self.identify_critical_feedback())
        
        # 4. Product-specific insights
        insights.extend(self.generate_product_insights())
        
        # 5. Trend analysis
        insights.extend(self.analyze_sentiment_trends())
        
        # 6. Urgency-based insights
        insights.extend(self.analyze_urgent_issues())
        
        logger.info(f"Generated {len(insights)} insights")
        
        return insights
    
    def detect_recurring_complaints(self) -> List[Dict[str, Any]]:
        """
        Detect recurring complaint topics.
        
        Returns:
            List of complaint insights
        """
        insights = []
        
        # Get negative feedbacks
        negative_feedbacks = self.get_queryset().filter(
            sentiment='negative'
        )
        
        if negative_feedbacks.count() < 3:
            return insights
        
        # Count topic occurrences
        topic_counter = Counter()
        topic_feedbacks = defaultdict(list)
        
        for feedback in negative_feedbacks:
            for topic in feedback.topics:
                topic_counter[topic] += 1
                topic_feedbacks[topic].append({
                    'id': feedback.raw_feed.id,
                    'text': feedback.raw_feed.text[:100],
                    'rating': feedback.raw_feed.rating
                })
        
        # Find recurring topics (appears in 20%+ of negative feedback)
        threshold = max(3, negative_feedbacks.count() * 0.2)
        
        for topic, count in topic_counter.most_common(10):
            if count >= threshold:
                percentage = (count / negative_feedbacks.count()) * 100
                
                insights.append({
                    'type': 'recurring_complaint',
                    'severity': self._calculate_severity(count, percentage),
                    'title': f"Recurring Complaint: {topic.title()}",
                    'description': (
                        f"{count} customers ({percentage:.1f}% of negative feedback) "
                        f"mentioned issues with '{topic}' in the last {self.days_back} days."
                    ),
                    'recommendation': self._generate_recommendation(topic, 'complaint'),
                    'metrics': {
                        'occurrences': count,
                        'percentage': round(percentage, 2),
                        'total_negative': negative_feedbacks.count()
                    },
                    'related_topics': [topic],
                    'sample_feedbacks': topic_feedbacks[topic][:3]
                })
        
        return insights
    
    def detect_recurring_praise(self) -> List[Dict[str, Any]]:
        """
        Detect recurring praise topics.
        
        Returns:
            List of praise insights
        """
        insights = []
        
        # Get positive feedbacks
        positive_feedbacks = self.get_queryset().filter(
            sentiment='positive'
        )
        
        if positive_feedbacks.count() < 3:
            return insights
        
        # Count topic occurrences
        topic_counter = Counter()
        
        for feedback in positive_feedbacks:
            for topic in feedback.topics:
                topic_counter[topic] += 1
        
        # Find recurring praise topics
        threshold = max(3, positive_feedbacks.count() * 0.2)
        
        for topic, count in topic_counter.most_common(5):
            if count >= threshold:
                percentage = (count / positive_feedbacks.count()) * 100
                
                insights.append({
                    'type': 'recurring_praise',
                    'severity': 'low',  # Praise is good news
                    'title': f"Strength: {topic.title()}",
                    'description': (
                        f"{count} customers ({percentage:.1f}% of positive feedback) "
                        f"praised '{topic}'. This is a key strength to maintain."
                    ),
                    'recommendation': f"Continue maintaining high standards for {topic}. Consider highlighting this in marketing.",
                    'metrics': {
                        'occurrences': count,
                        'percentage': round(percentage, 2),
                        'total_positive': positive_feedbacks.count()
                    },
                    'related_topics': [topic]
                })
        
        return insights
    
    def identify_critical_feedback(self) -> List[Dict[str, Any]]:
        """
        Identify critical negative feedback requiring immediate attention.
        
        Returns:
            List of critical insights
        """
        insights = []
        
        # Get critical feedback (negative + urgent + low rating)
        critical_feedbacks = self.get_queryset().filter(
            Q(sentiment='negative') & 
            Q(urgency__in=['high', 'critical']) |
            Q(raw_feed__rating=1)
        ).order_by('-processed_at')[:10]
        
        if critical_feedbacks.count() == 0:
            return insights
        
        # Group by urgency
        urgency_groups = defaultdict(list)
        for feedback in critical_feedbacks:
            urgency_groups[feedback.urgency].append({
                'id': feedback.raw_feed.id,
                'text': feedback.raw_feed.text[:150],
                'rating': feedback.raw_feed.rating,
                'product': feedback.raw_feed.product_name,
                'topics': feedback.topics,
                'processed_at': feedback.processed_at.isoformat()
            })
        
        # Create insights for each urgency level
        for urgency, feedbacks in urgency_groups.items():
            severity_map = {
                'critical': 'critical',
                'high': 'high',
                'medium': 'medium'
            }
            
            insights.append({
                'type': 'critical_feedback',
                'severity': severity_map.get(urgency, 'medium'),
                'title': f"{urgency.title()} Priority Issues Detected",
                'description': (
                    f"{len(feedbacks)} {urgency} priority issues require immediate attention. "
                    "These customers expressed strong dissatisfaction."
                ),
                'recommendation': "Reach out to affected customers immediately. Investigate root causes and implement fixes.",
                'metrics': {
                    'count': len(feedbacks),
                    'urgency_level': urgency,
                    'avg_rating': sum(f['rating'] for f in feedbacks if f['rating']) / len(feedbacks)
                },
                'related_topics': list(set(
                    topic for f in feedbacks for topic in f['topics']
                ))[:5],
                'sample_feedbacks': feedbacks[:3]
            })
        
        return insights
    
    def generate_product_insights(self) -> List[Dict[str, Any]]:
        """
        Generate product-specific insights.
        
        Returns:
            List of product insights
        """
        insights = []
        
        # Get feedbacks with product names
        product_feedbacks = self.get_queryset().filter(
            raw_feed__product_name__isnull=False
        ).exclude(raw_feed__product_name='')
        
        if product_feedbacks.count() < 5:
            return insights
        
        # Analyze by product
        products = product_feedbacks.values('raw_feed__product_name').annotate(
            total=Count('id'),
            avg_sentiment=Avg('sentiment_score'),
            negative_count=Count('id', filter=Q(sentiment='negative')),
            positive_count=Count('id', filter=Q(sentiment='positive'))
        ).order_by('-total')[:10]
        
        for product in products:
            product_name = product['raw_feed__product_name']
            total = product['total']
            avg_sentiment = product['avg_sentiment']
            negative_pct = (product['negative_count'] / total) * 100
            
            # Only create insights for products with significant feedback
            if total < 5:
                continue
            
            # Determine if product needs attention
            if negative_pct > 40 or avg_sentiment < 0.5:
                severity = 'high' if negative_pct > 60 else 'medium'
                
                # Get common issues
                product_negatives = product_feedbacks.filter(
                    raw_feed__product_name=product_name,
                    sentiment='negative'
                )
                
                common_topics = Counter()
                for fb in product_negatives:
                    for topic in fb.topics:
                        common_topics[topic] += 1
                
                top_issues = [topic for topic, _ in common_topics.most_common(3)]
                
                insights.append({
                    'type': 'product_issue',
                    'severity': severity,
                    'title': f"Product Alert: {product_name}",
                    'description': (
                        f"{product_name} has {negative_pct:.1f}% negative feedback "
                        f"({product['negative_count']}/{total} reviews). "
                        f"Common issues: {', '.join(top_issues) if top_issues else 'various'}"
                    ),
                    'recommendation': self._generate_product_recommendation(
                        product_name, top_issues
                    ),
                    'metrics': {
                        'total_feedback': total,
                        'negative_percentage': round(negative_pct, 2),
                        'avg_sentiment_score': round(avg_sentiment, 2),
                        'negative_count': product['negative_count'],
                        'positive_count': product['positive_count']
                    },
                    'related_topics': top_issues,
                    'product_name': product_name
                })
            
            # Highlight highly praised products
            elif negative_pct < 20 and avg_sentiment > 0.7:
                insights.append({
                    'type': 'product_success',
                    'severity': 'low',
                    'title': f"Top Performer: {product_name}",
                    'description': (
                        f"{product_name} is performing excellently with "
                        f"{product['positive_count']}/{total} positive reviews "
                        f"({(product['positive_count']/total)*100:.1f}%)."
                    ),
                    'recommendation': f"Use {product_name} as a model for other products. Consider increasing marketing focus.",
                    'metrics': {
                        'total_feedback': total,
                        'positive_percentage': round((product['positive_count']/total)*100, 2),
                        'avg_sentiment_score': round(avg_sentiment, 2)
                    },
                    'product_name': product_name
                })
        
        return insights
    
    def analyze_sentiment_trends(self) -> List[Dict[str, Any]]:
        """
        Analyze sentiment trends over time.
        
        Returns:
            List of trend insights
        """
        insights = []
        
        # Split time period in half
        midpoint = self.cutoff_date + timedelta(days=self.days_back/2)
        
        # First half
        first_half = self.get_queryset().filter(
            processed_at__lt=midpoint
        )
        
        # Second half
        second_half = self.get_queryset().filter(
            processed_at__gte=midpoint
        )
        
        if first_half.count() < 5 or second_half.count() < 5:
            return insights
        
        # Calculate metrics
        first_avg = first_half.aggregate(avg=Avg('sentiment_score'))['avg']
        second_avg = second_half.aggregate(avg=Avg('sentiment_score'))['avg']
        
        first_negative_pct = (first_half.filter(sentiment='negative').count() / first_half.count()) * 100
        second_negative_pct = (second_half.filter(sentiment='negative').count() / second_half.count()) * 100
        
        # Detect significant changes
        sentiment_change = second_avg - first_avg
        negative_change = second_negative_pct - first_negative_pct
        
        if abs(sentiment_change) > 0.1 or abs(negative_change) > 10:
            if sentiment_change < -0.1 or negative_change > 10:
                # Declining sentiment
                insights.append({
                    'type': 'sentiment_trend',
                    'severity': 'high',
                    'title': "Declining Customer Satisfaction",
                    'description': (
                        f"Sentiment has declined by {abs(sentiment_change)*100:.1f}% "
                        f"over the last {self.days_back} days. "
                        f"Negative feedback increased from {first_negative_pct:.1f}% to {second_negative_pct:.1f}%."
                    ),
                    'recommendation': "Investigate recent changes (product updates, policy changes, etc.). Address emerging issues quickly.",
                    'metrics': {
                        'sentiment_change': round(sentiment_change, 3),
                        'negative_change': round(negative_change, 2),
                        'first_period_avg': round(first_avg, 2),
                        'second_period_avg': round(second_avg, 2)
                    }
                })
            else:
                # Improving sentiment
                insights.append({
                    'type': 'sentiment_trend',
                    'severity': 'low',
                    'title': "Improving Customer Satisfaction",
                    'description': (
                        f"Great news! Sentiment has improved by {abs(sentiment_change)*100:.1f}% "
                        f"over the last {self.days_back} days. "
                        f"Negative feedback decreased from {first_negative_pct:.1f}% to {second_negative_pct:.1f}%."
                    ),
                    'recommendation': "Continue current strategies. Document what's working well for future reference.",
                    'metrics': {
                        'sentiment_change': round(sentiment_change, 3),
                        'negative_change': round(negative_change, 2),
                        'first_period_avg': round(first_avg, 2),
                        'second_period_avg': round(second_avg, 2)
                    }
                })
        
        return insights
    
    def analyze_urgent_issues(self) -> List[Dict[str, Any]]:
        """
        Analyze urgent issues requiring immediate action.
        
        Returns:
            List of urgency insights
        """
        insights = []
        
        # Get urgent feedbacks from last 7 days
        recent_cutoff = timezone.now() - timedelta(days=7)
        urgent_feedbacks = self.get_queryset().filter(
            urgency__in=['high', 'critical'],
            processed_at__gte=recent_cutoff
        )
        
        urgent_count = urgent_feedbacks.count()
        
        if urgent_count == 0:
            return insights
        
        # Count urgent topics
        topic_counter = Counter()
        for feedback in urgent_feedbacks:
            for topic in feedback.topics:
                topic_counter[topic] += 1
        
        top_urgent_topics = [topic for topic, _ in topic_counter.most_common(3)]
        
        insights.append({
            'type': 'urgent_action',
            'severity': 'critical',
            'title': f"{urgent_count} Urgent Issues in Past Week",
            'description': (
                f"{urgent_count} urgent issues detected in the last 7 days. "
                f"Top concerns: {', '.join(top_urgent_topics) if top_urgent_topics else 'various'}. "
                "Immediate action required."
            ),
            'recommendation': (
                "1. Review all urgent feedback immediately\n"
                "2. Contact affected customers within 24 hours\n"
                "3. Escalate to relevant teams\n"
                "4. Track resolution progress"
            ),
            'metrics': {
                'urgent_count': urgent_count,
                'timeframe_days': 7,
                'critical_count': urgent_feedbacks.filter(urgency='critical').count(),
                'high_count': urgent_feedbacks.filter(urgency='high').count()
            },
            'related_topics': top_urgent_topics
        })
        
        return insights
    
    def _calculate_severity(self, count: int, percentage: float) -> str:
        """Calculate insight severity based on metrics"""
        if percentage > 50 or count > 20:
            return 'critical'
        elif percentage > 30 or count > 10:
            return 'high'
        elif percentage > 15 or count > 5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendation(self, topic: str, feedback_type: str) -> str:
        """Generate contextual recommendation"""
        recommendations = {
            'delivery': "Review logistics processes. Consider partnering with faster shipping providers.",
            'quality': "Conduct quality assurance review. Inspect manufacturing processes.",
            'service': "Provide additional customer service training. Review response protocols.",
            'price': "Analyze pricing strategy. Consider competitor pricing and value proposition.",
            'packaging': "Review packaging materials and methods. Ensure adequate protection.",
            'performance': "Conduct technical performance testing. Optimize system resources.",
            'battery': "Test battery performance. Consider hardware or software optimizations.",
        }
        
        for key, rec in recommendations.items():
            if key in topic.lower():
                return rec
        
        return f"Investigate issues related to {topic}. Gather more customer feedback and implement targeted improvements."
    
    def _generate_product_recommendation(self, product: str, issues: List[str]) -> str:
        """Generate product-specific recommendation"""
        if not issues:
            return f"Review {product} for quality issues. Conduct customer interviews."
        
        issue_str = ', '.join(issues[:2])
        return (
            f"Priority actions for {product}:\n"
            f"1. Address {issue_str} immediately\n"
            f"2. Contact affected customers\n"
            f"3. Consider product recall if safety-critical\n"
            f"4. Improve quality control processes"
        )
    
    def save_insights(self, insights: List[Dict[str, Any]]) -> int:
        """
        Save generated insights to database.
        
        Args:
            insights: List of insight dictionaries
            
        Returns:
            Number of insights saved
        """
        saved_count = 0
        
        for insight_data in insights:
            try:
                # Check if similar insight already exists
                existing = Insight.objects.filter(
                    entity_id=self.entity_id,
                    type=insight_data['type'],
                    title=insight_data['title'],
                    created_at__gte=timezone.now() - timedelta(days=1)
                ).first()
                
                if existing:
                    # Update existing
                    for key, value in insight_data.items():
                        setattr(existing, key, value)
                    existing.save()
                else:
                    # Create new
                    Insight.objects.create(
                        entity_id=self.entity_id,
                        **insight_data
                    )
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save insight: {str(e)}")
        
        logger.info(f"Saved {saved_count} insights")
        return saved_count


def generate_insights_for_entity(entity_id: int, days_back: int = 30) -> Dict[str, Any]:
    """
    Generate and save insights for a specific entity.
    
    Args:
        entity_id: Entity ID
        days_back: Number of days to analyze
        
    Returns:
        Summary of generated insights
    """
    generator = InsightsGenerator(entity_id=entity_id, days_back=days_back)
    insights = generator.generate_all_insights()
    saved_count = generator.save_insights(insights)
    
    # Group by type
    by_type = defaultdict(int)
    by_severity = defaultdict(int)
    
    for insight in insights:
        by_type[insight['type']] += 1
        by_severity[insight['severity']] += 1
    
    return {
        'total_generated': len(insights),
        'total_saved': saved_count,
        'by_type': dict(by_type),
        'by_severity': dict(by_severity),
        'entity_id': entity_id,
        'days_analyzed': days_back
    }