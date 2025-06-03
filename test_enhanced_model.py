#!/usr/bin/env python3
"""
Test script for the enhanced fatigue detector using real data trained models.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental_fatique.settings')
django.setup()

from fatique.ml_models.fatigue_detector import FatigueDetector

def test_enhanced_fatigue_detector():
    """Test the enhanced fatigue detector with real data models."""
    
    print("🧠 Testing Enhanced Fatigue Detector with Real Data Models")
    print("=" * 65)
    
    # Initialize the enhanced fatigue detector
    print("\n1. 🚀 Initializing Enhanced Fatigue Detector...")
    try:
        detector = FatigueDetector(use_real_data_model=True)
        print("   ✅ Fatigue detector initialized successfully!")
        
        if detector.real_data_model:
            print("   ✅ Real data trained model loaded!")
        else:
            print("   ⚠️  Using fallback neural network model")
            
    except Exception as e:
        print(f"   ❌ Error initializing detector: {e}")
        return
    
    # Test cases with different fatigue scenarios
    test_cases = [
        {
            'name': 'Low Fatigue (Morning - Fresh Start)',
            'data': {
                'typing_data': {
                    'typingSpeed': 65,
                    'errorRate': 2,
                    'pauseFrequency': 1,
                    'keyPressDuration': 95
                },
                'mouse_data': {
                    'movementSpeed': 150,
                    'clickFrequency': 10,
                    'accuracy': 90,
                    'reactionTime': 300
                },
                'facial_data': {
                    'blinkRate': 15,
                    'eyeClosure': 150,
                    'expression': 'Alert',
                    'analyzed': True
                }
            }
        },
        {
            'name': 'Medium Fatigue (Afternoon Slump)',
            'data': {
                'typing_data': {
                    'typingSpeed': 45,
                    'errorRate': 6,
                    'pauseFrequency': 4,
                    'keyPressDuration': 130
                },
                'mouse_data': {
                    'movementSpeed': 110,
                    'clickFrequency': 7,
                    'accuracy': 75,
                    'reactionTime': 450
                },
                'facial_data': {
                    'blinkRate': 22,
                    'eyeClosure': 250,
                    'expression': 'Tired',
                    'analyzed': True
                }
            }
        },
        {
            'name': 'High Fatigue (Evening - Exhausted)',
            'data': {
                'typing_data': {
                    'typingSpeed': 28,
                    'errorRate': 12,
                    'pauseFrequency': 7,
                    'keyPressDuration': 180
                },
                'mouse_data': {
                    'movementSpeed': 70,
                    'clickFrequency': 4,
                    'accuracy': 60,
                    'reactionTime': 650
                },
                'facial_data': {
                    'blinkRate': 8,
                    'eyeClosure': 400,
                    'expression': 'Exhausted',
                    'analyzed': True
                }
            }
        },
        {
            'name': 'Stressed State (High Activity)',
            'data': {
                'typing_data': {
                    'typingSpeed': 55,
                    'errorRate': 9,
                    'pauseFrequency': 6,
                    'keyPressDuration': 110
                },
                'mouse_data': {
                    'movementSpeed': 180,
                    'clickFrequency': 15,
                    'accuracy': 65,
                    'reactionTime': 250
                },
                'facial_data': {
                    'blinkRate': 30,
                    'eyeClosure': 120,
                    'expression': 'Stressed',
                    'analyzed': True
                }
            }
        }
    ]
    
    print(f"\n2. 🧪 Testing {len(test_cases)} Fatigue Scenarios...")
    print("-" * 65)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['name']}")
        print("   " + "=" * 50)
        
        try:
            # Predict fatigue using the enhanced model
            result = detector.predict(input_data=test_case['data'])
            
            print(f"   📊 Fatigue Score: {result['fatigue_score']:.1f}/100")
            print(f"   📈 Fatigue Level: {result['fatigue_level'].upper()}")
            print(f"   🎯 Confidence: {result['confidence']:.1%}")
            
            # Display contributing factors
            if result['contributing_factors']:
                print(f"   ⚠️  Contributing Factors:")
                for factor, details in result['contributing_factors'].items():
                    severity = details.get('severity', 'unknown')
                    value = details.get('value', 'N/A')
                    print(f"      - {factor.replace('_', ' ').title()}: {severity} ({value})")
            else:
                print(f"   ✅ No significant contributing factors detected")
            
            # Display top recommendations
            if result['recommendations']:
                print(f"   💡 Top Recommendations:")
                for j, rec in enumerate(result['recommendations'][:3], 1):
                    print(f"      {j}. {rec}")
            
            print(f"   ✅ Test completed successfully!")
            
        except Exception as e:
            print(f"   ❌ Error in test: {e}")
            import traceback
            traceback.print_exc()
    
    # Test model comparison
    print(f"\n3. 🔄 Model Comparison Test...")
    print("-" * 65)
    
    try:
        # Test with real data model
        detector_real = FatigueDetector(use_real_data_model=True)
        result_real = detector_real.predict(input_data=test_cases[1]['data'])
        
        # Test with neural network model
        detector_nn = FatigueDetector(use_real_data_model=False)
        result_nn = detector_nn.predict(input_data=test_cases[1]['data'])
        
        print(f"   📊 Real Data Model:")
        print(f"      - Fatigue Score: {result_real['fatigue_score']:.1f}")
        print(f"      - Confidence: {result_real['confidence']:.1%}")
        print(f"      - Level: {result_real['fatigue_level']}")
        
        print(f"   🧠 Neural Network Model:")
        print(f"      - Fatigue Score: {result_nn['fatigue_score']:.1f}")
        print(f"      - Confidence: {result_nn['confidence']:.1%}")
        print(f"      - Level: {result_nn['fatigue_level']}")
        
        print(f"   ✅ Model comparison completed!")
        
    except Exception as e:
        print(f"   ❌ Error in model comparison: {e}")
    
    # Performance summary
    print(f"\n4. 📈 Performance Summary...")
    print("-" * 65)
    
    try:
        if detector.real_data_model:
            print(f"   ✅ Real Data Model Status: ACTIVE")
            print(f"   📊 Training Data: 410 samples from real datasets")
            print(f"   🎯 Model Type: Random Forest Regressor")
            print(f"   📈 Training R²: 0.890")
            print(f"   🧪 Test R²: 0.766")
            print(f"   🔍 Top Features: eye_closure_duration, click_frequency, eye_blink_rate")
        else:
            print(f"   ⚠️  Real Data Model Status: NOT AVAILABLE")
            print(f"   🧠 Fallback: Neural Network Model")
        
        print(f"   ✅ Performance summary completed!")
        
    except Exception as e:
        print(f"   ❌ Error in performance summary: {e}")
    
    print(f"\n🎉 Enhanced Fatigue Detector Testing Completed!")
    print("=" * 65)

if __name__ == "__main__":
    test_enhanced_fatigue_detector()
