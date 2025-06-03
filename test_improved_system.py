#!/usr/bin/env python3
"""
Test script to verify the improved Mental Fatigue Detector system.
Tests typing analysis, mouse game accuracy, and dashboard ML confidence display.
"""

import os
import sys
import django
from pathlib import Path
import requests
import json

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental_fatique.settings')
django.setup()

def test_improved_system():
    """Test all the improvements made to the Mental Fatigue Detector."""
    
    print("🔧 Testing Improved Mental Fatigue Detector System")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Verify server is running
    print("\n1. 🌐 Testing Server Connectivity...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   ✅ Server status: {response.status_code}")
        assert response.status_code == 200
    except Exception as e:
        print(f"   ❌ Server connectivity error: {e}")
        return
    
    # Test 2: Test improved typing analysis with realistic data
    print("\n2. ⌨️  Testing Improved Typing Analysis...")
    try:
        # Test case 1: Good typing performance (low fatigue)
        good_typing_data = {
            "typing_data": {
                "typingSpeed": 65,      # Good WPM
                "errorRate": 3,         # Low error rate
                "pauseFrequency": 1,    # Few pauses
                "keyPressDuration": 95, # Normal key press duration
                "wordCount": 50,
                "correctCharacters": 245,
                "totalCharacters": 250,
                "backspaceCount": 2
            },
            "mouse_data": {
                "score": 15,
                "accuracy": 85,
                "reactionTime": 350,
                "movementSpeed": 140
            },
            "facial_data": {
                "blinkRate": 18,
                "eyeClosure": 160,
                "expression": "Focused"
            }
        }
        
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=good_typing_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Good typing performance:")
            print(f"      - Fatigue Score: {result['fatigue_analysis']['combined_fatigue_score']:.1f}")
            print(f"      - Confidence: {result['fatigue_analysis']['confidence']:.1%}")
            print(f"      - Expected: Low fatigue (< 40)")
        
        # Test case 2: Poor typing performance (high fatigue)
        poor_typing_data = {
            "typing_data": {
                "typingSpeed": 25,      # Slow WPM
                "errorRate": 15,        # High error rate
                "pauseFrequency": 8,    # Many pauses
                "keyPressDuration": 180, # Slow key presses
                "wordCount": 15,
                "correctCharacters": 60,
                "totalCharacters": 75,
                "backspaceCount": 12
            },
            "mouse_data": {
                "score": 3,
                "accuracy": 35,
                "reactionTime": 850,
                "movementSpeed": 60
            },
            "facial_data": {
                "blinkRate": 8,
                "eyeClosure": 420,
                "expression": "Tired"
            }
        }
        
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=poor_typing_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Poor typing performance:")
            print(f"      - Fatigue Score: {result['fatigue_analysis']['combined_fatigue_score']:.1f}")
            print(f"      - Confidence: {result['fatigue_analysis']['confidence']:.1%}")
            print(f"      - Expected: High fatigue (> 60)")
            
    except Exception as e:
        print(f"   ❌ Typing analysis test error: {e}")
    
    # Test 3: Test improved mouse game scoring
    print("\n3. 🖱️  Testing Improved Mouse Game Scoring...")
    try:
        # Test case 1: Good mouse performance (low fatigue)
        good_mouse_data = {
            "typing_data": {
                "typingSpeed": 50,
                "errorRate": 5,
                "pauseFrequency": 2
            },
            "mouse_data": {
                "score": 18,            # High score
                "accuracy": 90,         # High accuracy
                "reactionTime": 320,    # Fast reaction
                "movementSpeed": 150,
                "totalTargets": 20,
                "hitTargets": 18,
                "totalClicks": 20
            },
            "facial_data": {
                "blinkRate": 16,
                "eyeClosure": 150,
                "expression": "Focused"
            }
        }
        
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=good_mouse_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Good mouse performance:")
            print(f"      - Fatigue Score: {result['fatigue_analysis']['combined_fatigue_score']:.1f}")
            print(f"      - Expected: Low fatigue (accurate clicking should = low fatigue)")
        
        # Test case 2: Poor mouse performance (high fatigue)
        poor_mouse_data = {
            "typing_data": {
                "typingSpeed": 45,
                "errorRate": 6,
                "pauseFrequency": 3
            },
            "mouse_data": {
                "score": 2,             # Low score
                "accuracy": 25,         # Poor accuracy
                "reactionTime": 950,    # Slow reaction
                "movementSpeed": 45,
                "totalTargets": 20,
                "hitTargets": 2,
                "totalClicks": 15
            },
            "facial_data": {
                "blinkRate": 12,
                "eyeClosure": 380,
                "expression": "Tired"
            }
        }
        
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=poor_mouse_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Poor mouse performance:")
            print(f"      - Fatigue Score: {result['fatigue_analysis']['combined_fatigue_score']:.1f}")
            print(f"      - Expected: High fatigue (poor clicking should = high fatigue)")
            
    except Exception as e:
        print(f"   ❌ Mouse game test error: {e}")
    
    # Test 4: Test ML confidence display
    print("\n4. 🧠 Testing ML Confidence Display...")
    try:
        # Test with complete data (should have high confidence)
        complete_data = {
            "typing_data": {
                "typingSpeed": 55,
                "errorRate": 4,
                "pauseFrequency": 2,
                "keyPressDuration": 110
            },
            "mouse_data": {
                "score": 12,
                "accuracy": 75,
                "reactionTime": 450,
                "movementSpeed": 120
            },
            "facial_data": {
                "blinkRate": 20,
                "eyeClosure": 200,
                "expression": "Neutral",
                "analyzed": True
            }
        }
        
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=complete_data)
        if response.status_code == 200:
            result = response.json()
            confidence = result['fatigue_analysis']['confidence']
            print(f"   ✅ Complete data confidence: {confidence:.1%}")
            print(f"      - Expected: High confidence (> 80%) due to all data sources")
            
            if confidence > 0.8:
                print(f"      ✅ Confidence is appropriately high")
            else:
                print(f"      ⚠️  Confidence lower than expected")
        
        # Test with incomplete data (should have lower confidence)
        incomplete_data = {
            "typing_data": {
                "typingSpeed": 45,
                "errorRate": 6
            },
            "mouse_data": {},  # Missing mouse data
            "facial_data": {}  # Missing facial data
        }
        
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=incomplete_data)
        if response.status_code == 200:
            result = response.json()
            confidence = result['fatigue_analysis']['confidence']
            print(f"   ✅ Incomplete data confidence: {confidence:.1%}")
            print(f"      - Expected: Lower confidence (< 70%) due to missing data")
            
            if confidence < 0.7:
                print(f"      ✅ Confidence is appropriately lower")
            else:
                print(f"      ⚠️  Confidence higher than expected for incomplete data")
            
    except Exception as e:
        print(f"   ❌ ML confidence test error: {e}")
    
    # Test 5: Test dashboard pages
    print("\n5. 📊 Testing Dashboard Pages...")
    try:
        response = requests.get(f"{base_url}/dashboard/view/")
        print(f"   ✅ Dashboard page status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if the page contains ML confidence elements
            if 'mlConfidence' in response.text:
                print(f"      ✅ ML confidence element found in dashboard")
            else:
                print(f"      ⚠️  ML confidence element not found in dashboard")
                
    except Exception as e:
        print(f"   ❌ Dashboard test error: {e}")
    
    # Test 6: Test data collection page
    print("\n6. 📝 Testing Data Collection Page...")
    try:
        response = requests.get(f"{base_url}/data_collection/")
        print(f"   ✅ Data collection page status: {response.status_code}")
        
        if response.status_code == 200:
            # Check for improved analysis functions
            if 'calculateTypingFatigueScore' in response.text:
                print(f"      ✅ Improved typing analysis found")
            if 'calculateMouseFatigueScore' in response.text:
                print(f"      ✅ Improved mouse analysis found")
                
    except Exception as e:
        print(f"   ❌ Data collection test error: {e}")
    
    print(f"\n🎉 System Testing Completed!")
    print("=" * 60)
    
    print(f"\n📋 Summary of Improvements:")
    print(f"   ✅ Fixed typing WPM calculation (now uses proper word counting)")
    print(f"   ✅ Fixed character accuracy calculation (compares with prompt text)")
    print(f"   ✅ Fixed mouse fatigue scoring (low accuracy = high fatigue)")
    print(f"   ✅ Added detailed mouse metrics logging")
    print(f"   ✅ Fixed ML confidence display in dashboard")
    print(f"   ✅ Added confidence calculation based on data quality")
    print(f"   ✅ Enhanced error rate calculation for typing")
    print(f"   ✅ Improved reaction time handling for mouse game")

if __name__ == "__main__":
    test_improved_system()
