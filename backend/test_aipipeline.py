"""
Test script for AI Processor with real HuggingFace models.
Run this to verify all AI models are working.

Usage:
    python test_ai_models.py
"""

import os
import django
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from analysis.ai_processor import get_ai_processor

# Colors
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


# Test samples
TEST_SAMPLES = [
    {
        'text': "This product is absolutely amazing! The quality is excellent and delivery was super fast. Highly recommend!",
        'expected_sentiment': 'positive',
        'expected_topics': ['quality', 'delivery', 'product']
    },
    {
        'text': "Terrible experience. The product arrived broken and customer service was unresponsive. Very disappointed.",
        'expected_sentiment': 'negative',
        'expected_topics': ['product', 'service', 'delivery']
    },
    {
        'text': "The product is okay. Nothing special but does the job. Average quality for the price.",
        'expected_sentiment': 'neutral',
        'expected_topics': ['product', 'quality', 'price']
    },
    {
        'text': "URGENT: The system is completely broken and not working. We need immediate assistance! Critical issue!",
        'expected_sentiment': 'negative',
        'expected_urgency': 'critical'
    }
]


def test_model_loading():
    """Test that models load successfully"""
    print("\n" + "="*60)
    log("🚀 Testing Model Loading", BLUE)
    print("="*60)
    
    try:
        log("\nInitializing AI Processor...", YELLOW)
        start = time.time()
        
        processor = get_ai_processor()
        
        load_time = time.time() - start
        
        log(f"✅ AI Processor loaded in {load_time:.2f}s", GREEN)
        
        # Check which models loaded
        models_status = {
            'Sentiment': processor.sentiment_analyzer is not None,
            'Topics': processor.topic_extractor is not None,
            'Summarization': processor.summarizer is not None,
            'Embeddings': processor.embedding_model is not None,
            'Urgency': processor.urgency_classifier is not None,
        }
        
        log("\nModels Status:", YELLOW)
        for model, loaded in models_status.items():
            status = "✅ Loaded" if loaded else "❌ Failed"
            color = GREEN if loaded else RED
            log(f"  {model}: {status}", color)
        
        return all(models_status.values())
        
    except Exception as e:
        log(f"❌ Failed to load models: {str(e)}", RED)
        import traceback
        traceback.print_exc()
        return False


def test_sentiment_analysis():
    """Test sentiment analysis"""
    print("\n" + "="*60)
    log("📊 Testing Sentiment Analysis (Day 8)", BLUE)
    print("="*60)
    
    processor = get_ai_processor()
    passed = 0
    
    for i, sample in enumerate(TEST_SAMPLES[:3], 1):
        log(f"\nSample {i}:", YELLOW)
        log(f"Text: {sample['text'][:80]}...", YELLOW)
        
        try:
            result = processor.analyze_sentiment(sample['text'])
            
            log(f"Sentiment: {result['label']}", GREEN)
            log(f"Score: {result['score']:.3f}", GREEN)
            log(f"Confidence: {result['confidence']:.3f}", GREEN)
            
            # Check if matches expected
            expected = sample.get('expected_sentiment')
            if expected and result['label'] == expected:
                log(f"✅ Matches expected: {expected}", GREEN)
                passed += 1
            elif expected:
                log(f"⚠️  Expected {expected}, got {result['label']}", YELLOW)
            else:
                passed += 1
            
        except Exception as e:
            log(f"❌ Error: {str(e)}", RED)
    
    log(f"\n✅ Sentiment tests: {passed}/3 passed", GREEN if passed == 3 else YELLOW)
    return passed == 3


def test_topic_extraction():
    """Test topic extraction"""
    print("\n" + "="*60)
    log("🏷️  Testing Topic Extraction (Day 9)", BLUE)
    print("="*60)
    
    processor = get_ai_processor()
    passed = 0
    
    for i, sample in enumerate(TEST_SAMPLES[:3], 1):
        log(f"\nSample {i}:", YELLOW)
        log(f"Text: {sample['text'][:80]}...", YELLOW)
        
        try:
            topics = processor.extract_topics(sample['text'])
            
            log(f"Extracted topics: {', '.join(topics)}", GREEN)
            
            # Check if any expected topics found
            expected = sample.get('expected_topics', [])
            if expected:
                found = any(exp in ' '.join(topics).lower() for exp in expected)
                if found:
                    log(f"✅ Found expected topics", GREEN)
                    passed += 1
                else:
                    log(f"⚠️  Expected topics: {expected}", YELLOW)
            else:
                passed += 1
            
        except Exception as e:
            log(f"❌ Error: {str(e)}", RED)
    
    log(f"\n✅ Topic extraction tests: {passed}/3 passed", GREEN if passed == 3 else YELLOW)
    return passed >= 2


def test_summarization():
    """Test summarization"""
    print("\n" + "="*60)
    log("📝 Testing Summarization (Day 10)", BLUE)
    print("="*60)
    
    processor = get_ai_processor()
    
    long_text = """
    This product exceeded all my expectations. The build quality is outstanding,
    with premium materials used throughout. The performance is excellent - very
    fast and responsive. Delivery was prompt and the packaging was secure. The
    customer service team was helpful when I had questions. The price point is
    very competitive for the quality you get. I've been using it for two weeks
    now and haven't encountered any issues. Battery life is impressive, lasting
    all day with heavy use. The design is sleek and modern. Would definitely
    recommend this to friends and family. Overall, a fantastic purchase that I'm
    very happy with.
    """
    
    log("\nOriginal text length:", YELLOW)
    log(f"{len(long_text)} characters", YELLOW)
    
    try:
        summary = processor.summarize(long_text, max_length=100)
        
        log("\nGenerated summary:", GREEN)
        log(f"{summary}", GREEN)
        log(f"\nSummary length: {len(summary)} characters", GREEN)
        
        if len(summary) < len(long_text):
            log("✅ Summary is shorter than original", GREEN)
            return True
        else:
            log("⚠️  Summary is not shorter", YELLOW)
            return False
        
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
        return False


def test_embeddings():
    """Test embedding generation"""
    print("\n" + "="*60)
    log("🔢 Testing Embeddings (Day 11)", BLUE)
    print("="*60)
    
    processor = get_ai_processor()
    
    text = "This is a test sentence for generating embeddings."
    
    log(f"\nText: {text}", YELLOW)
    
    try:
        embeddings = processor.generate_embeddings(text)
        
        log(f"Embedding dimensions: {len(embeddings)}", GREEN)
        log(f"Sample values: {embeddings[:5]}", GREEN)
        log(f"Type: {type(embeddings[0])}", GREEN)
        
        if len(embeddings) == 384:  # all-MiniLM-L6-v2 produces 384-dim
            log("✅ Correct embedding dimension (384)", GREEN)
            return True
        else:
            log(f"⚠️  Unexpected dimension: {len(embeddings)}", YELLOW)
            return False
        
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
        return False


def test_urgency_classification():
    """Test urgency classification"""
    print("\n" + "="*60)
    log("🚨 Testing Urgency Classification (Bonus)", BLUE)
    print("="*60)
    
    processor = get_ai_processor()
    
    urgent_sample = TEST_SAMPLES[3]
    
    log(f"\nText: {urgent_sample['text'][:80]}...", YELLOW)
    
    try:
        result = processor.classify_urgency(urgent_sample['text'])
        
        log(f"Urgency: {result['urgency']}", GREEN)
        log(f"Score: {result['score']:.3f}", GREEN)
        log(f"Reasoning: {result['reasoning']}", GREEN)
        
        expected = urgent_sample.get('expected_urgency')
        if result['urgency'] in ['high', 'critical']:
            log(f"✅ Correctly identified as urgent", GREEN)
            return True
        else:
            log(f"⚠️  Expected urgent, got {result['urgency']}", YELLOW)
            return False
        
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
        return False


def test_complete_pipeline():
    """Test complete processing pipeline"""
    print("\n" + "="*60)
    log("🔄 Testing Complete Pipeline (Days 12-13)", BLUE)
    print("="*60)
    
    processor = get_ai_processor()
    
    sample = TEST_SAMPLES[0]
    
    log(f"\nProcessing: {sample['text'][:80]}...", YELLOW)
    
    try:
        start = time.time()
        result = processor.process_feedback_complete(sample['text'])
        duration = time.time() - start
        
        log(f"\n✅ Complete processing in {duration:.2f}s", GREEN)
        
        log("\nResults:", YELLOW)
        log(f"  Sentiment: {result['sentiment']} ({result['sentiment_score']:.3f})", GREEN)
        log(f"  Topics: {', '.join(result['topics'])}", GREEN)
        log(f"  Summary: {result['summary'][:80]}...", GREEN)
        log(f"  Embeddings: {len(result['embeddings'])} dimensions", GREEN)
        log(f"  Urgency: {result['urgency']} ({result['urgency_score']:.3f})", GREEN)
        log(f"  Key phrases: {', '.join(result['key_phrases'])}", GREEN)
        
        # Verify all fields present
        required_fields = ['sentiment', 'topics', 'summary', 'embeddings', 'urgency']
        all_present = all(field in result for field in required_fields)
        
        if all_present:
            log("\n✅ All fields present in result", GREEN)
            return True
        else:
            log("\n⚠️  Some fields missing", YELLOW)
            return False
        
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    log("🧪 AI Processor Test Suite (Days 8-13)", BLUE)
    print("="*60)
    
    log("\n⚠️  Note: First run will download models (~500MB)", YELLOW)
    log("This may take 2-5 minutes depending on your internet speed.", YELLOW)
    log("Subsequent runs will be fast (models cached).\n", YELLOW)
    
    results = {}
    
    # Test 1: Model loading
    results['loading'] = test_model_loading()
    
    if not results['loading']:
        log("\n❌ Model loading failed. Cannot proceed with other tests.", RED)
        return
    
    # Test 2: Sentiment
    results['sentiment'] = test_sentiment_analysis()
    
    # Test 3: Topics
    results['topics'] = test_topic_extraction()
    
    # Test 4: Summarization
    results['summarization'] = test_summarization()
    
    # Test 5: Embeddings
    results['embeddings'] = test_embeddings()
    
    # Test 6: Urgency
    results['urgency'] = test_urgency_classification()
    
    # Test 7: Complete pipeline
    results['pipeline'] = test_complete_pipeline()
    
    # Summary
    print("\n" + "="*60)
    log("📋 Test Summary", BLUE)
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        color = GREEN if passed else RED
        log(f"{test_name.upper()}: {status}", color)
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print("\n" + "="*60)
    log(f"Results: {passed_count}/{total_count} tests passed", BLUE)
    
    if passed_count == total_count:
        log("🎉 All AI models working perfectly!", GREEN)
        log("\nYou're ready to:", YELLOW)
        print("1. Run migrations: python manage.py makemigrations && python manage.py migrate")
        print("2. Update Celery task to use process_feedback_with_ai")
        print("3. Process real feedbacks with AI!")
    elif passed_count >= 5:
        log("✅ Core AI functionality working!", GREEN)
        log("⚠️  Some optional features need attention", YELLOW)
    else:
        log("⚠️  Multiple tests failed. Check errors above.", YELLOW)
        log("\nCommon fixes:", YELLOW)
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Check internet connection (models download on first run)")
        print("3. Ensure sufficient disk space (~1GB for models)")
    
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