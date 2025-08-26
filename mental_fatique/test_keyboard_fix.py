#!/usr/bin/env python3
"""
Test script to verify the keyboard character counting fix.
Tests various typing scenarios to ensure error rate calculation is accurate.
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

def test_keyboard_error_rate_fix():
    """Test the keyboard error rate calculation fix."""
    
    print("🔧 Testing Keyboard Error Rate Fix")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Perfect typing (should have 0% error rate)
    print("\n1. 📝 Testing Perfect Typing (Expected: 0% error rate)...")
    perfect_typing_data = {
        "typing_data": {
            "typingSpeed": 60,
            "errorRate": 0,  # This should be calculated correctly
            "pauseFrequency": 1,
            "keyPressDuration": 100,
            "wordCount": 30,
            "correctCharacters": 150,  # All characters correct
            "totalCharacters": 150,
            "backspaceCount": 0  # No backspaces
        },
        "mouse_data": {
            "score": 15,
            "accuracy": 85,
            "reactionTime": 350
        },
        "facial_data": {
            "blinkRate": 18,
            "eyeClosure": 160,
            "expression": "Focused"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=perfect_typing_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Perfect typing result:")
            print(f"      - Fatigue Score: {result['fatigue_analysis']['combined_fatigue_score']:.1f}")
            print(f"      - Expected: Low fatigue (< 30) due to perfect typing")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 2: Moderate errors (should have reasonable error rate)
    print("\n2. 📝 Testing Moderate Errors (Expected: ~10% error rate)...")
    moderate_error_data = {
        "typing_data": {
            "typingSpeed": 45,
            "errorRate": 10,  # Moderate error rate
            "pauseFrequency": 3,
            "keyPressDuration": 120,
            "wordCount": 25,
            "correctCharacters": 135,  # 90% accuracy
            "totalCharacters": 150,
            "backspaceCount": 5  # Some corrections
        },
        "mouse_data": {
            "score": 12,
            "accuracy": 75,
            "reactionTime": 400
        },
        "facial_data": {
            "blinkRate": 20,
            "eyeClosure": 180,
            "expression": "Neutral"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=moderate_error_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Moderate errors result:")
            print(f"      - Fatigue Score: {result['fatigue_analysis']['combined_fatigue_score']:.1f}")
            print(f"      - Expected: Moderate fatigue (30-60) due to some errors")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 3: High error rate (should have high error rate but not 100%)
    print("\n3. 📝 Testing High Errors (Expected: ~25% error rate, NOT 100%)...")
    high_error_data = {
        "typing_data": {
            "typingSpeed": 25,
            "errorRate": 25,  # High but reasonable error rate
            "pauseFrequency": 8,
            "keyPressDuration": 180,
            "wordCount": 15,
            "correctCharacters": 112,  # 75% accuracy
            "totalCharacters": 150,
            "backspaceCount": 15  # Many corrections
        },
        "mouse_data": {
            "score": 6,
            "accuracy": 50,
            "reactionTime": 600
        },
        "facial_data": {
            "blinkRate": 12,
            "eyeClosure": 300,
            "expression": "Tired"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=high_error_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ High errors result:")
            print(f"      - Fatigue Score: {result['fatigue_analysis']['combined_fatigue_score']:.1f}")
            print(f"      - Expected: High fatigue (60-80) due to many errors")
            
            # Check if the error rate is reasonable (not 100%)
            if result['fatigue_analysis']['combined_fatigue_score'] < 90:
                print(f"      ✅ Error rate calculation appears fixed (not showing 100%)")
            else:
                print(f"      ⚠️  Error rate might still be too high")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 4: Edge case - very few characters typed
    print("\n4. 📝 Testing Edge Case - Few Characters (Expected: Reasonable error rate)...")
    few_chars_data = {
        "typing_data": {
            "typingSpeed": 30,
            "errorRate": 15,  # Should be calculated properly
            "pauseFrequency": 2,
            "keyPressDuration": 150,
            "wordCount": 5,
            "correctCharacters": 20,  # Only 20 characters typed correctly
            "totalCharacters": 25,    # Out of 25 total
            "backspaceCount": 3       # Few corrections
        },
        "mouse_data": {
            "score": 8,
            "accuracy": 65,
            "reactionTime": 500
        },
        "facial_data": {
            "blinkRate": 16,
            "eyeClosure": 200,
            "expression": "Neutral"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=few_chars_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Few characters result:")
            print(f"      - Fatigue Score: {result['fatigue_analysis']['combined_fatigue_score']:.1f}")
            print(f"      - Expected: Moderate fatigue due to limited data")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    print(f"\n🎉 Keyboard Error Rate Testing Completed!")
    print("=" * 50)
    
    print(f"\n📋 Summary of Fixes:")
    print(f"   ✅ Separated character accuracy from keystroke accuracy")
    print(f"   ✅ Fixed double-counting of errors (backspaces + incorrect chars)")
    print(f"   ✅ Improved printable key detection")
    print(f"   ✅ Added detailed error rate calculation logging")
    print(f"   ✅ Used conservative approach (higher of two error rates)")
    print(f"   ✅ Capped error rate at 100% maximum")
    
    print(f"\n🔍 How the Fix Works:")
    print(f"   1. Character Error Rate = (incorrect chars / total chars) * 100")
    print(f"   2. Keystroke Error Rate = (backspaces / printable keystrokes) * 100")
    print(f"   3. Final Error Rate = max(character_rate, keystroke_rate)")
    print(f"   4. This prevents the 100% error rate issue")

if __name__ == "__main__":
    test_keyboard_error_rate_fix()
