"""
Test script for Insights & Analytics System (Week 3)
Run this to verify insights generation and analytics endpoints work.

Usage:
    python test_insights_system.py
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

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


def test_insights_system():
    """Test all insights and analytics endpoints"""
    
    print("\n" + "="*60)
    log("🧪 Testing Insights & Analytics System (Week 3)", BLUE)
    print("="*60 + "\n")
    
    # First, login and get token
    log("🔑 Logging in...", YELLOW)
    login_response = requests.post(
        f"{API_BASE}/users/login/",
        json={
            "username": "testuser",  # Adjust as needed
            "password": "test1user"   # Adjust as needed
        }
    )
    
    if login_response.status_code != 200:
        log("❌ Login failed. Please create a test user first.", RED)
        return
    
    access_token = login_response.json()['access']
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    log(f"✅ Logged in successfully", GREEN)
    
    # Get entity ID (assumes you have at least one entity)
    log("\n📋 Getting entity...", YELLOW)
    entities_response = requests.get(
        f"{API_BASE}/data-ingestion/entities/",
        headers=headers
    )
    
    if entities_response.status_code != 200 or not entities_response.json().get('results'):
        log("❌ No entities found. Please create an entity first.", RED)
        return
    
    entity_id = entities_response.json()['results'][0]['id']
    log(f"✅ Using entity ID: {entity_id}", GREEN)
    
    # Test 1: Generate Insights
    print("\n" + "="*60)
    log("📊 Test 1: Generate Insights", BLUE)
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_BASE}/analysis/insights/generate/",
            headers=headers,
            json={
                "entity_id": entity_id,
                "days_back": 30
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Insights generated successfully", GREEN)
            log(f"   Total generated: {data.get('total_generated', 0)}", GREEN)
            log(f"   Total saved: {data.get('total_saved', 0)}", GREEN)
            log(f"   By type: {data.get('by_type', {})}", GREEN)
            log(f"   By severity: {data.get('by_severity', {})}", GREEN)
        else:
            log(f"⚠️  Insight generation returned: {response.status_code}", YELLOW)
            log(f"   Response: {response.text}", YELLOW)
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
    
    # Test 2: List Insights
    print("\n" + "="*60)
    log("📋 Test 2: List Insights", BLUE)
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_BASE}/analysis/insights/?entity_id={entity_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            insights = data.get('results', data)
            log(f"✅ Retrieved {len(insights)} insights", GREEN)
            
            if insights:
                log("\n   Sample insights:", YELLOW)
                for insight in insights[:3]:
                    log(f"   - [{insight['severity_display']}] {insight['title']}", GREEN)
        else:
            log(f"❌ Failed: {response.text}", RED)
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
    
    # Test 3: Insight Summary
    print("\n" + "="*60)
    log("📊 Test 3: Insight Summary", BLUE)
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_BASE}/analysis/insights/summary/?entity_id={entity_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Insight summary retrieved", GREEN)
            log(f"   Total: {data.get('total', 0)}", GREEN)
            log(f"   Active: {data.get('active', 0)}", GREEN)
            log(f"   Resolved: {data.get('resolved', 0)}", GREEN)
            log(f"   By severity: {data.get('by_severity', {})}", GREEN)
        else:
            log(f"❌ Failed: {response.text}", RED)
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
    
    # Test 4: Dashboard Analytics
    print("\n" + "="*60)
    log("📈 Test 4: Dashboard Analytics", BLUE)
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_BASE}/analysis/dashboard/?entity_id={entity_id}&days=30",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Dashboard analytics retrieved", GREEN)
            log(f"   Total feedbacks: {data.get('total_feedbacks', 0)}", GREEN)
            log(f"   Average sentiment: {data.get('average_sentiment', 0):.2f}", GREEN)
            log(f"   Active insights: {data.get('active_insights_count', 0)}", GREEN)
            log(f"   Critical insights: {data.get('critical_insights_count', 0)}", GREEN)
            
            sentiment = data.get('sentiment_breakdown', {})
            if sentiment:
                log(f"\n   Sentiment breakdown:", YELLOW)
                for sent, info in sentiment.items():
                    log(f"     {sent}: {info.get('count', 0)} ({info.get('percentage', 0):.1f}%)", GREEN)
            
            top_topics = data.get('top_topics', [])
            if top_topics:
                log(f"\n   Top topics:", YELLOW)
                for topic in top_topics[:5]:
                    log(f"     {topic['topic']}: {topic['count']} mentions", GREEN)
        else:
            log(f"❌ Failed: {response.text}", RED)
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
    
    # Test 5: Sentiment Statistics
    print("\n" + "="*60)
    log("📊 Test 5: Sentiment Statistics", BLUE)
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_BASE}/analysis/processed-feedbacks/sentiment_stats/?entity_id={entity_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Sentiment stats retrieved", GREEN)
            log(f"   Total processed: {data.get('total_processed', 0)}", GREEN)
            log(f"   Positive: {data.get('positive_count', 0)} ({data.get('positive_percentage', 0):.1f}%)", GREEN)
            log(f"   Neutral: {data.get('neutral_count', 0)} ({data.get('neutral_percentage', 0):.1f}%)", GREEN)
            log(f"   Negative: {data.get('negative_count', 0)} ({data.get('negative_percentage', 0):.1f}%)", GREEN)
        else:
            log(f"❌ Failed: {response.text}", RED)
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
    
    # Test 6: Filter Insights by Severity
    print("\n" + "="*60)
    log("🔍 Test 6: Filter Insights (High Priority)", BLUE)
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_BASE}/analysis/insights/?entity_id={entity_id}&severity=high&is_resolved=false",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            insights = data.get('results', data)
            log(f"✅ Found {len(insights)} high priority insights", GREEN)
            
            for insight in insights[:3]:
                log(f"   - {insight['title']}", YELLOW)
        else:
            log(f"❌ Failed: {response.text}", RED)
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
    
    # Test 7: Export CSV
    print("\n" + "="*60)
    log("📥 Test 7: Export Feedbacks to CSV", BLUE)
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_BASE}/analysis/processed-feedbacks/export_csv/?entity_id={entity_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            filename = f"test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'wb') as f:
                f.write(response.content)
            log(f"✅ CSV exported successfully: {filename}", GREEN)
        else:
            log(f"❌ Failed: {response.text}", RED)
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
    
    # Test 8: Topic Analytics (if topics exist)
    print("\n" + "="*60)
    log("🏷️  Test 8: Topic Analytics", BLUE)
    print("="*60)
    
    try:
        # Get top topics first
        dashboard_response = requests.get(
            f"{API_BASE}/analysis/dashboard/?entity_id={entity_id}",
            headers=headers
        )
        
        if dashboard_response.status_code == 200:
            top_topics = dashboard_response.json().get('top_topics', [])
            
            if top_topics:
                topic = top_topics[0]['topic']
                log(f"   Analyzing topic: '{topic}'", YELLOW)
                
                response = requests.get(
                    f"{API_BASE}/analysis/topics/{topic}/?entity_id={entity_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    log(f"✅ Topic analytics retrieved", GREEN)
                    log(f"   Total mentions: {data.get('total_mentions', 0)}", GREEN)
                    log(f"   Average rating: {data.get('average_rating', 'N/A')}", GREEN)
                else:
                    log(f"⚠️  Topic analytics: {response.status_code}", YELLOW)
            else:
                log("   ℹ️  No topics found for analysis", YELLOW)
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
    
    # Test 9: Resolve Insight (if insights exist)
    print("\n" + "="*60)
    log("✅ Test 9: Resolve Insight", BLUE)
    print("="*60)
    
    try:
        # Get first insight
        insights_response = requests.get(
            f"{API_BASE}/analysis/insights/?entity_id={entity_id}&is_resolved=false",
            headers=headers
        )
        
        if insights_response.status_code == 200:
            insights = insights_response.json().get('results', [])
            
            if insights:
                insight_id = insights[0]['id']
                
                response = requests.post(
                    f"{API_BASE}/analysis/insights/{insight_id}/resolve/",
                    headers=headers,
                    json={
                        "notes": "Addressed by implementing process improvements"
                    }
                )
                
                if response.status_code == 200:
                    log(f"✅ Insight #{insight_id} resolved successfully", GREEN)
                else:
                    log(f"❌ Failed: {response.text}", RED)
            else:
                log("   ℹ️  No unresolved insights to test with", YELLOW)
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)
    
    # Summary
    print("\n" + "="*60)
    log("✅ Insights & Analytics Testing Complete!", GREEN)
    print("="*60 + "\n")
    
    log("📚 Available Endpoints:", YELLOW)
    print("1. POST   /api/analysis/insights/generate/")
    print("2. GET    /api/analysis/insights/")
    print("3. GET    /api/analysis/insights/summary/")
    print("4. GET    /api/analysis/insights/{id}/")
    print("5. POST   /api/analysis/insights/{id}/resolve/")
    print("6. GET    /api/analysis/dashboard/")
    print("7. GET    /api/analysis/processed-feedbacks/")
    print("8. GET    /api/analysis/processed-feedbacks/sentiment_stats/")
    print("9. GET    /api/analysis/processed-feedbacks/export_csv/")
    print("10. GET   /api/analysis/topics/{topic}/")
    print("11. GET   /api/analysis/products/{product}/")
    print()


if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get(BASE_URL, timeout=2)
        test_insights_system()
    except requests.exceptions.ConnectionError:
        log("❌ Cannot connect to server. Make sure Django is running:", RED)
        log("   python manage.py runserver", YELLOW)
    except Exception as e:
        log(f"❌ Error: {str(e)}", RED)