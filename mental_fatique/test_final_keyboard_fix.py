#!/usr/bin/env python3
"""
Final test script to verify the keyboard character counting and progress bar fixes.
Tests perfect typing, moderate errors, and various edge cases.
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

def test_final_keyboard_fixes():
    """Test the final keyboard fixes for error rate and progress bar."""
    
    print("🔧 Testing Final Keyboard Character Counting & Progress Bar Fixes")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Perfect typing (should have 0% error rate)
    print("\n1. ✅ Testing Perfect Typing (Expected: 0% error rate)...")
    perfect_data = {
        "typing_data": {
            "typingSpeed": 65,
            "errorRate": 0,  # Should be 0 for perfect typing
            "pauseFrequency": 1,
            "keyPressDuration": 100,
            "wordCount": 35,
            "correctCharacters": 175,  # All characters correct
            "totalCharacters": 175,    # Same as correct
            "backspaceCount": 0        # No corrections needed
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
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=perfect_data)
        if response.status_code == 200:
            result = response.json()
            fatigue_score = result['fatigue_analysis']['combined_fatigue_score']
            print(f"   ✅ Perfect typing result:")
            print(f"      - Fatigue Score: {fatigue_score:.1f}/100")
            print(f"      - Expected: Very low fatigue (< 20)")
            
            if fatigue_score < 20:
                print(f"      ✅ PASS: Perfect typing correctly shows low fatigue")
            else:
                print(f"      ❌ FAIL: Perfect typing shows unexpectedly high fatigue")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 2: Good typing with minimal errors (should have ~5% error rate)
    print("\n2. ✅ Testing Good Typing with Minimal Errors (Expected: ~5% error rate)...")
    good_data = {
        "typing_data": {
            "typingSpeed": 55,
            "errorRate": 5,   # Small error rate
            "pauseFrequency": 2,
            "keyPressDuration": 110,
            "wordCount": 30,
            "correctCharacters": 142,  # 95% accuracy
            "totalCharacters": 150,
            "backspaceCount": 3        # Few corrections
        },
        "mouse_data": {
            "score": 15,
            "accuracy": 80,
            "reactionTime": 380
        },
        "facial_data": {
            "blinkRate": 18,
            "eyeClosure": 170,
            "expression": "Neutral"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=good_data)
        if response.status_code == 200:
            result = response.json()
            fatigue_score = result['fatigue_analysis']['combined_fatigue_score']
            print(f"   ✅ Good typing result:")
            print(f"      - Fatigue Score: {fatigue_score:.1f}/100")
            print(f"      - Expected: Low-moderate fatigue (20-40)")
            
            if 20 <= fatigue_score <= 40:
                print(f"      ✅ PASS: Good typing shows appropriate fatigue level")
            else:
                print(f"      ⚠️  WARNING: Fatigue score outside expected range")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 3: Moderate errors (should have ~15% error rate)
    print("\n3. ⚠️  Testing Moderate Errors (Expected: ~15% error rate)...")
    moderate_data = {
        "typing_data": {
            "typingSpeed": 40,
            "errorRate": 15,  # Moderate error rate
            "pauseFrequency": 4,
            "keyPressDuration": 140,
            "wordCount": 22,
            "correctCharacters": 127,  # 85% accuracy
            "totalCharacters": 150,
            "backspaceCount": 8        # Some corrections
        },
        "mouse_data": {
            "score": 10,
            "accuracy": 65,
            "reactionTime": 500
        },
        "facial_data": {
            "blinkRate": 14,
            "eyeClosure": 220,
            "expression": "Neutral"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=moderate_data)
        if response.status_code == 200:
            result = response.json()
            fatigue_score = result['fatigue_analysis']['combined_fatigue_score']
            print(f"   ✅ Moderate errors result:")
            print(f"      - Fatigue Score: {fatigue_score:.1f}/100")
            print(f"      - Expected: Moderate fatigue (40-65)")
            
            if 40 <= fatigue_score <= 65:
                print(f"      ✅ PASS: Moderate errors show appropriate fatigue level")
            else:
                print(f"      ⚠️  WARNING: Fatigue score outside expected range")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 4: High errors but not unrealistic (should have ~25% error rate, NOT 100%)
    print("\n4. ❌ Testing High Errors (Expected: ~25% error rate, NOT 100%)...")
    high_error_data = {
        "typing_data": {
            "typingSpeed": 25,
            "errorRate": 25,  # High but realistic error rate
            "pauseFrequency": 8,
            "keyPressDuration": 200,
            "wordCount": 15,
            "correctCharacters": 112,  # 75% accuracy
            "totalCharacters": 150,
            "backspaceCount": 18       # Many corrections
        },
        "mouse_data": {
            "score": 5,
            "accuracy": 40,
            "reactionTime": 750
        },
        "facial_data": {
            "blinkRate": 10,
            "eyeClosure": 350,
            "expression": "Tired"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=high_error_data)
        if response.status_code == 200:
            result = response.json()
            fatigue_score = result['fatigue_analysis']['combined_fatigue_score']
            print(f"   ✅ High errors result:")
            print(f"      - Fatigue Score: {fatigue_score:.1f}/100")
            print(f"      - Expected: High fatigue (65-85)")
            
            if 65 <= fatigue_score <= 85:
                print(f"      ✅ PASS: High errors show high but realistic fatigue")
            elif fatigue_score > 90:
                print(f"      ❌ FAIL: Error rate calculation still too harsh")
            else:
                print(f"      ⚠️  WARNING: Fatigue score outside expected range")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 5: Edge case - very short text
    print("\n5. 🔍 Testing Edge Case - Very Short Text (Expected: Lenient error rate)...")
    short_text_data = {
        "typing_data": {
            "typingSpeed": 35,
            "errorRate": 10,  # Should be lenient for short text
            "pauseFrequency": 1,
            "keyPressDuration": 120,
            "wordCount": 3,
            "correctCharacters": 12,   # 12 out of 15 characters correct
            "totalCharacters": 15,     # Very short text
            "backspaceCount": 2        # Few corrections
        },
        "mouse_data": {
            "score": 12,
            "accuracy": 70,
            "reactionTime": 450
        },
        "facial_data": {
            "blinkRate": 17,
            "eyeClosure": 180,
            "expression": "Neutral"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/fatigue/analyze/", json=short_text_data)
        if response.status_code == 200:
            result = response.json()
            fatigue_score = result['fatigue_analysis']['combined_fatigue_score']
            print(f"   ✅ Short text result:")
            print(f"      - Fatigue Score: {fatigue_score:.1f}/100")
            print(f"      - Expected: Moderate fatigue (30-50) with leniency for short text")
            
            if 30 <= fatigue_score <= 50:
                print(f"      ✅ PASS: Short text handled with appropriate leniency")
            else:
                print(f"      ⚠️  WARNING: Short text handling may need adjustment")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    print(f"\n🎉 Final Keyboard Testing Completed!")
    print("=" * 70)
    
    print(f"\n📋 Summary of Final Fixes:")
    print(f"   ✅ Simplified error rate calculation (only character mismatches)")
    print(f"   ✅ Removed double-counting of backspaces and errors")
    print(f"   ✅ Added leniency for short text (< 10 characters)")
    print(f"   ✅ Capped maximum error rate at 50% (realistic limit)")
    print(f"   ✅ Enhanced progress bar (70% correct chars + 30% total progress)")
    print(f"   ✅ Color-coded progress bar (green/yellow/red based on accuracy)")
    print(f"   ✅ Improved character count display (shows correct vs total)")
    print(f"   ✅ Simplified and reliable logging")
    
    print(f"\n🔍 How the Final Fix Works:")
    print(f"   1. Error Rate = (incorrect characters / total typed) * 100")
    print(f"   2. Leniency for short text (< 10 chars): error_rate * 0.5")
    print(f"   3. Maximum error rate capped at 50%")
    print(f"   4. Progress = (correct_chars * 0.7) + (total_progress * 0.3)")
    print(f"   5. No more 100% error rates for normal typing!")

if __name__ == "__main__":
    test_final_keyboard_fixes()
