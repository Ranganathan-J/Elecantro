"""
AI Processing Module with Real HuggingFace Models
Days 8-13: Complete AI Pipeline

This module provides:
1. Sentiment Analysis (Day 8)
2. Topic Extraction (Day 9)
3. Summarization (Day 10)
4. Embeddings (Day 11)
5. Urgency Classification (Bonus)
"""

import logging
from typing import Dict, List, Any, Optional
import torch
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModel
)
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
import numpy as np

logger = logging.getLogger(__name__)


class AIProcessor:
    """
    Main AI processor with HuggingFace models.
    Singleton pattern to load models once and reuse.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize all models (happens once)"""
        if self._initialized:
            return
        
        logger.info("🚀 Initializing AI Processor...")
        
        # Determine device (GPU if available)
        self.device = 0 if torch.cuda.is_available() else -1
        logger.info(f"Using device: {'GPU' if self.device == 0 else 'CPU'}")
        
        # Initialize models
        self._init_sentiment_model()
        self._init_topic_model()
        self._init_summarization_model()
        self._init_embedding_model()
        self._init_urgency_model()
        
        self._initialized = True
        logger.info("✅ AI Processor initialized successfully!")
    
    def _init_sentiment_model(self):
        """Initialize sentiment analysis model (Day 8)"""
        try:
            logger.info("Loading sentiment model...")
            
            # Using DistilBERT for sentiment (fast and accurate)
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=self.device
            )
            
            logger.info("✅ Sentiment model loaded")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            self.sentiment_analyzer = None
    
    def _init_topic_model(self):
        """Initialize topic extraction model (Day 9)"""
        try:
            logger.info("Loading topic extraction model...")
            
            # KeyBERT for keyword/topic extraction
            self.topic_extractor = KeyBERT(model='all-MiniLM-L6-v2')
            
            logger.info("✅ Topic extraction model loaded")
        except Exception as e:
            logger.error(f"Failed to load topic model: {e}")
            self.topic_extractor = None
    
    def _init_summarization_model(self):
        """Initialize summarization model (Day 10)"""
        try:
            logger.info("Loading summarization model...")
            
            # Using T5-small for summarization (good balance of speed/quality)
            self.summarizer = pipeline(
                "summarization",
                model="t5-small",
                device=self.device,
                max_length=150,
                min_length=30
            )
            
            logger.info("✅ Summarization model loaded")
        except Exception as e:
            logger.error(f"Failed to load summarization model: {e}")
            self.summarizer = None
    
    def _init_embedding_model(self):
        """Initialize embedding model (Day 11)"""
        try:
            logger.info("Loading embedding model...")
            
            # Sentence transformers for embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("✅ Embedding model loaded")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def _init_urgency_model(self):
        """Initialize urgency classification model (Bonus)"""
        try:
            logger.info("Loading urgency classifier...")
            
            # Using zero-shot classification for urgency
            self.urgency_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=self.device
            )
            
            logger.info("✅ Urgency classifier loaded")
        except Exception as e:
            logger.error(f"Failed to load urgency classifier: {e}")
            self.urgency_classifier = None
    
    # ==================== DAY 8: SENTIMENT ANALYSIS ====================
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using HuggingFace model.
        
        Args:
            text: Input text to analyze
            
        Returns:
            {
                'label': 'positive' | 'negative' | 'neutral',
                'score': 0.0-1.0,
                'raw_label': 'POSITIVE' | 'NEGATIVE',
                'confidence': 0.0-1.0
            }
        """
        try:
            if not self.sentiment_analyzer:
                return self._fallback_sentiment(text)
            
            # Truncate text if too long (512 token limit)
            text = text[:512]
            
            # Get prediction
            result = self.sentiment_analyzer(text)[0]
            
            # Map labels
            label_map = {
                'POSITIVE': 'positive',
                'NEGATIVE': 'negative',
                'LABEL_1': 'positive',
                'LABEL_0': 'negative'
            }
            
            label = label_map.get(result['label'], 'neutral')
            score = result['score']
            
            logger.info(f"Sentiment: {label} ({score:.2f})")
            
            return {
                'label': label,
                'score': score,
                'raw_label': result['label'],
                'confidence': score
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return self._fallback_sentiment(text)
    
    def _fallback_sentiment(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using keywords"""
        text_lower = text.lower()
        
        positive_words = ['great', 'excellent', 'amazing', 'love', 'perfect', 'good', 'best', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'poor', 'disappointed', 'horrible']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return {'label': 'positive', 'score': 0.7, 'raw_label': 'POSITIVE', 'confidence': 0.7}
        elif neg_count > pos_count:
            return {'label': 'negative', 'score': 0.7, 'raw_label': 'NEGATIVE', 'confidence': 0.7}
        else:
            return {'label': 'neutral', 'score': 0.5, 'raw_label': 'NEUTRAL', 'confidence': 0.5}
    
    # ==================== DAY 9: TOPIC EXTRACTION ====================
    
    def extract_topics(self, text: str, top_n: int = 5) -> List[str]:
        """
        Extract topics/keywords using KeyBERT.
        
        Args:
            text: Input text
            top_n: Number of topics to extract
            
        Returns:
            List of topic strings
        """
        try:
            if not self.topic_extractor:
                return self._fallback_topics(text, top_n)
            
            # Extract keywords with KeyBERT
            keywords = self.topic_extractor.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                stop_words='english',
                top_n=top_n,
                use_mmr=True,
                diversity=0.5
            )
            
            # Extract just the words (not scores)
            topics = [kw[0] for kw in keywords]
            
            logger.info(f"Extracted topics: {topics}")
            
            return topics
            
        except Exception as e:
            logger.error(f"Topic extraction error: {e}")
            return self._fallback_topics(text, top_n)
    
    def _fallback_topics(self, text: str, top_n: int) -> List[str]:
        """Fallback topic extraction using simple keywords"""
        text_lower = text.lower()
        
        # Common topics
        topic_keywords = {
            'delivery': ['delivery', 'shipping', 'arrived', 'late', 'fast'],
            'quality': ['quality', 'product', 'build', 'material'],
            'price': ['price', 'cost', 'expensive', 'cheap', 'value'],
            'service': ['service', 'support', 'help', 'customer'],
            'packaging': ['package', 'box', 'packaging', 'wrapped'],
            'performance': ['performance', 'speed', 'fast', 'slow'],
        }
        
        found_topics = []
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                found_topics.append(topic)
        
        return found_topics[:top_n] if found_topics else ['general']
    
    # ==================== DAY 10: SUMMARIZATION ====================
    
    def summarize(self, text: str, max_length: int = 150) -> str:
        """
        Generate summary of text using T5.
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summary string
        """
        try:
            # Only summarize if text is long enough
            if len(text) < 100:
                return text
            
            if not self.summarizer:
                return self._fallback_summary(text, max_length)
            
            # Prepare text for T5
            text_to_summarize = text[:1024]  # T5 has token limit
            
            # Generate summary
            summary = self.summarizer(
                text_to_summarize,
                max_length=max_length,
                min_length=30,
                do_sample=False
            )[0]['summary_text']
            
            logger.info(f"Generated summary: {summary[:50]}...")
            
            return summary
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return self._fallback_summary(text, max_length)
    
    def _fallback_summary(self, text: str, max_length: int) -> str:
        """Fallback: just truncate"""
        return text[:max_length] + '...' if len(text) > max_length else text
    
    # ==================== DAY 11: EMBEDDINGS ====================
    
    def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate vector embeddings for text.
        
        Args:
            text: Input text
            
        Returns:
            List of floats (384-dimensional vector)
        """
        try:
            if not self.embedding_model:
                return self._fallback_embeddings()
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(
                text,
                convert_to_tensor=False,
                show_progress_bar=False
            )
            
            # Convert to list
            embedding_list = embeddings.tolist()
            
            logger.info(f"Generated embeddings: {len(embedding_list)} dimensions")
            
            return embedding_list
            
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return self._fallback_embeddings()
    
    def _fallback_embeddings(self) -> List[float]:
        """Fallback: random embeddings"""
        return np.random.random(384).tolist()
    
    # ==================== BONUS: URGENCY CLASSIFICATION ====================
    
    def classify_urgency(self, text: str) -> Dict[str, Any]:
        """
        Classify urgency level of feedback.
        
        Args:
            text: Input text
            
        Returns:
            {
                'urgency': 'low' | 'medium' | 'high' | 'critical',
                'score': 0.0-1.0,
                'reasoning': str
            }
        """
        try:
            if not self.urgency_classifier:
                return self._fallback_urgency(text)
            
            # Candidate labels for urgency
            candidate_labels = [
                "urgent problem requiring immediate attention",
                "moderate issue that needs addressing",
                "minor feedback or suggestion",
                "general comment or praise"
            ]
            
            result = self.urgency_classifier(
                text,
                candidate_labels,
                multi_label=False
            )
            
            # Map to urgency levels
            label_to_urgency = {
                candidate_labels[0]: 'critical',
                candidate_labels[1]: 'high',
                candidate_labels[2]: 'medium',
                candidate_labels[3]: 'low'
            }
            
            top_label = result['labels'][0]
            urgency = label_to_urgency.get(top_label, 'medium')
            score = result['scores'][0]
            
            logger.info(f"Urgency: {urgency} ({score:.2f})")
            
            return {
                'urgency': urgency,
                'score': score,
                'reasoning': top_label
            }
            
        except Exception as e:
            logger.error(f"Urgency classification error: {e}")
            return self._fallback_urgency(text)
    
    def _fallback_urgency(self, text: str) -> Dict[str, Any]:
        """Fallback urgency classification"""
        text_lower = text.lower()
        
        critical_words = ['urgent', 'emergency', 'critical', 'immediately', 'asap', 'broken', 'not working']
        high_words = ['problem', 'issue', 'bug', 'error', 'failed', 'wrong']
        
        if any(word in text_lower for word in critical_words):
            return {'urgency': 'critical', 'score': 0.9, 'reasoning': 'Contains urgent keywords'}
        elif any(word in text_lower for word in high_words):
            return {'urgency': 'high', 'score': 0.7, 'reasoning': 'Contains problem keywords'}
        else:
            return {'urgency': 'low', 'score': 0.5, 'reasoning': 'General feedback'}
    
    # ==================== DAY 12-13: COMPLETE PIPELINE ====================
    
    def process_feedback_complete(self, text: str) -> Dict[str, Any]:
        """
        Complete pipeline: sentiment + topics + summary + embeddings + urgency.
        
        Args:
            text: Input feedback text
            
        Returns:
            Dictionary with all analysis results
        """
        logger.info(f"Processing feedback: {text[:50]}...")
        
        # Run all analyses
        sentiment = self.analyze_sentiment(text)
        topics = self.extract_topics(text)
        summary = self.summarize(text)
        embeddings = self.generate_embeddings(text)
        urgency = self.classify_urgency(text)
        
        # Extract key phrases (combination of topics)
        key_phrases = topics[:3]
        
        result = {
            'sentiment': sentiment['label'],
            'sentiment_score': sentiment['score'],
            'topics': topics,
            'summary': summary,
            'embeddings': embeddings,
            'key_phrases': key_phrases,
            'urgency': urgency['urgency'],
            'urgency_score': urgency['score'],
            'model_version': 'huggingface_v1.0'
        }
        
        logger.info(f"✅ Processing complete: {sentiment['label']} | {len(topics)} topics | {urgency['urgency']}")
        
        return result


# Singleton instance
_processor_instance = None


def get_ai_processor() -> AIProcessor:
    """
    Get the singleton AI processor instance.
    Models are loaded once and reused.
    """
    global _processor_instance
    
    if _processor_instance is None:
        _processor_instance = AIProcessor()
    
    return _processor_instance


# ==================== CONVENIENCE FUNCTIONS ====================

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Convenience function for sentiment analysis"""
    return get_ai_processor().analyze_sentiment(text)


def extract_topics(text: str, top_n: int = 5) -> List[str]:
    """Convenience function for topic extraction"""
    return get_ai_processor().extract_topics(text, top_n)


def summarize(text: str, max_length: int = 150) -> str:
    """Convenience function for summarization"""
    return get_ai_processor().summarize(text, max_length)


def generate_embeddings(text: str) -> List[float]:
    """Convenience function for embeddings"""
    return get_ai_processor().generate_embeddings(text)


def classify_urgency(text: str) -> Dict[str, Any]:
    """Convenience function for urgency classification"""
    return get_ai_processor().classify_urgency(text)


def process_complete(text: str) -> Dict[str, Any]:
    """Convenience function for complete pipeline"""
    return get_ai_processor().process_feedback_complete(text)