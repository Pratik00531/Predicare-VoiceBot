"""
Test the FastAPI backend endpoints
Run this to verify your API is working correctly
"""

import requests
import json
import base64

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_text_analysis():
    """Test medical analysis with text only"""
    print("🧠 Testing medical analysis...")
    
    data = {
        "query": "I have a headache and feel dizzy"
    }
    
    response = requests.post(f"{BASE_URL}/analyze", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Analysis: {result['analysis']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_speech_synthesis():
    """Test text-to-speech"""
    print("🔊 Testing speech synthesis...")
    
    data = {
        "text": "Hello, this is a test of the speech synthesis system."
    }
    
    response = requests.post(f"{BASE_URL}/synthesize", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Audio URL: {result['audio_url']}")
        print(f"Full URL: {BASE_URL}{result['audio_url']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_api_documentation():
    """Test if API documentation is accessible"""
    print("📚 Testing API documentation...")
    
    docs_response = requests.get(f"{BASE_URL}/docs")
    print(f"Docs Status: {docs_response.status_code}")
    
    root_response = requests.get(f"{BASE_URL}/")
    print(f"Root endpoint: {root_response.json()}")
    print()

if __name__ == "__main__":
    print("🚀 Testing Predicare VoiceBot API")
    print("=" * 50)
    
    try:
        test_health_check()
        test_api_documentation()
        test_text_analysis()
        test_speech_synthesis()
        
        print("✅ All tests completed!")
        print(f"🌐 API Documentation: {BASE_URL}/docs")
        print(f"🔧 API Root: {BASE_URL}/")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
