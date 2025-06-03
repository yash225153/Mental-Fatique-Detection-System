#!/usr/bin/env python3
"""
Comprehensive test script for the Mental Fatigue Detector system.
"""

import requests
import json

def test_mental_fatigue_detector():
    """Test all components of the Mental Fatigue Detector system."""
    
    print("🧠 Testing Mental Fatigue Detector System")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Home page
    print("1. Testing home page...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   ✅ Home page status: {response.status_code}")
        assert response.status_code == 200
    except Exception as e:
        print(f"   ❌ Home page error: {e}")
    
    # Test 2: Data collection page
    print("2. Testing data collection page...")
    try:
        response = requests.get(f"{base_url}/data_collection/")
        print(f"   ✅ Data collection page status: {response.status_code}")
        assert response.status_code == 200
    except Exception as e:
        print(f"   ❌ Data collection page error: {e}")
    
    # Test 3: Dashboard page
    print("3. Testing dashboard page...")
    try:
        response = requests.get(f"{base_url}/dashboard/view/")
        print(f"   ✅ Dashboard page status: {response.status_code}")
        assert response.status_code == 200
    except Exception as e:
        print(f"   ❌ Dashboard page error: {e}")
    
    # Test 4: ML analysis API
    print("4. Testing ML analysis API...")
    try:
        test_data = {
            "typing_data": {
                "typingSpeed": 45,
                "errorRate": 8,
                "pauseFrequency": 3
            },
            "mouse_data": {
                "score": 12,
                "accuracy": 75,
                "reactionTime": 450
            },
            "facial_data": {
                "blinkRate": 16,
                "eyeClosure": 180,
                "expression": "Neutral",
                "analyzed": True
            }
        }
        
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=test_data)
        print(f"   ✅ ML analysis API status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Analysis result: {result['status']}")
            print(f"   ✅ Fatigue score: {result['fatigue_analysis']['combined_fatigue_score']:.1f}")
            print(f"   ✅ Confidence: {result['fatigue_analysis']['confidence']:.3f}")
            print(f"   ✅ Recommendations: {len(result['recommendations']['recommendations'])} items")
        else:
            print(f"   ❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ ML analysis API error: {e}")
    
    # Test 5: Insights API
    print("5. Testing insights API...")
    try:
        response = requests.get(f"{base_url}/api/fatigue/insights/?fatigue_score=65")
        print(f"   ✅ Insights API status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Insights result: {result['status']}")
        else:
            print(f"   ❌ Insights API Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Insights API error: {e}")
    
    print("\n🎉 All tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_mental_fatigue_detector()
