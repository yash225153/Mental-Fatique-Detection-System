#!/usr/bin/env python3
"""
Test script to verify the character counting and progress bar fixes.
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

def test_character_counting_fix():
    """Test the character counting and progress calculation fixes."""
    
    print("🔧 Testing Character Counting & Progress Bar Fixes")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Simulate the user's scenario (62 typed, 7 correct)
    print("\n1. 🐛 Testing User's Scenario (62 typed, 7 correct)...")
    user_scenario_data = {
        "typing_data": {
            "typingSpeed": 30,
            "errorRate": 89,  # High error rate from the scenario
            "pauseFrequency": 5,
            "keyPressDuration": 150,
            "wordCount": 12,
            "correctCharacters": 7,    # Only 7 correct
            "totalCharacters": 62,     # 62 total typed
            "backspaceCount": 10
        },
        "mouse_data": {
            "score": 8,
            "accuracy": 60,
            "reactionTime": 500
        },
        "facial_data": {
            "blinkRate": 15,
            "eyeClosure": 250,
            "expression": "Neutral"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=user_scenario_data)
        if response.status_code == 200:
            result = response.json()
            fatigue_score = result['fatigue_analysis']['combined_fatigue_score']
            print(f"   ✅ User scenario result:")
            print(f"      - Fatigue Score: {fatigue_score:.1f}/100")
            print(f"      - Expected: High fatigue due to many errors")
            print(f"      - Progress should be: ~16% (62/369 characters attempted)")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 2: Good typing scenario
    print("\n2. ✅ Testing Good Typing (Should show proper progress)...")
    good_typing_data = {
        "typing_data": {
            "typingSpeed": 55,
            "errorRate": 5,
            "pauseFrequency": 2,
            "keyPressDuration": 110,
            "wordCount": 25,
            "correctCharacters": 95,   # 95 correct out of 100
            "totalCharacters": 100,    # 100 total typed
            "backspaceCount": 3
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
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=good_typing_data)
        if response.status_code == 200:
            result = response.json()
            fatigue_score = result['fatigue_analysis']['combined_fatigue_score']
            print(f"   ✅ Good typing result:")
            print(f"      - Fatigue Score: {fatigue_score:.1f}/100")
            print(f"      - Expected: Low fatigue due to good accuracy")
            print(f"      - Progress should be: ~27% + accuracy bonus (100/369 characters)")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 3: Perfect typing scenario
    print("\n3. 🎯 Testing Perfect Typing (Should show 0% error rate)...")
    perfect_typing_data = {
        "typing_data": {
            "typingSpeed": 65,
            "errorRate": 0,
            "pauseFrequency": 1,
            "keyPressDuration": 100,
            "wordCount": 30,
            "correctCharacters": 150,  # All correct
            "totalCharacters": 150,    # Same as correct
            "backspaceCount": 0
        },
        "mouse_data": {
            "score": 18,
            "accuracy": 90,
            "reactionTime": 320
        },
        "facial_data": {
            "blinkRate": 16,
            "eyeClosure": 150,
            "expression": "Focused"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=perfect_typing_data)
        if response.status_code == 200:
            result = response.json()
            fatigue_score = result['fatigue_analysis']['combined_fatigue_score']
            print(f"   ✅ Perfect typing result:")
            print(f"      - Fatigue Score: {fatigue_score:.1f}/100")
            print(f"      - Expected: Very low fatigue (< 15)")
            print(f"      - Progress should be: ~40% + 20% accuracy bonus (150/369 characters)")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    print(f"\n🎉 Character Counting Fix Testing Completed!")
    print("=" * 60)
    
    print(f"\n📋 Summary of Fixes Applied:")
    print(f"   ✅ Text normalization (trim + normalize whitespace)")
    print(f"   ✅ Improved progress calculation (typing progress + accuracy bonus)")
    print(f"   ✅ Fixed character comparison logic")
    print(f"   ✅ Enhanced progress bar formula")
    print(f"   ✅ Better character count display")
    print(f"   ✅ Detailed debugging logs")
    
    print(f"\n🔍 New Progress Calculation:")
    print(f"   1. Typing Progress = (typed_chars / total_prompt_chars) * 100")
    print(f"   2. Accuracy Bonus = accuracy * 20% (up to 20% bonus)")
    print(f"   3. Final Progress = min(typing_progress + accuracy_bonus, 100%)")
    print(f"   4. Minimum Progress = typing_progress * 50% (even with errors)")
    
    print(f"\n🎯 Expected Results:")
    print(f"   - User's scenario (62/369, 7 correct): ~16% progress")
    print(f"   - Good typing (100/369, 95 correct): ~27% + bonus")
    print(f"   - Perfect typing (150/369, all correct): ~40% + 20% bonus")

if __name__ == "__main__":
    test_character_counting_fix()
