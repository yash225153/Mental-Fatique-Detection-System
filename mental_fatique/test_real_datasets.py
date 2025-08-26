#!/usr/bin/env python3
"""
Test script to load and process real datasets for the Mental Fatigue Detector.
This script will test the integration of keyboard, mouse, and facial datasets.
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

from fatique.datasets.data_integrator import DataIntegrator
import pandas as pd
import numpy as np

def test_real_datasets():
    """Test loading and processing of real datasets."""
    
    print("🧠 Testing Real Datasets for Mental Fatigue Detector")
    print("=" * 60)
    
    # Initialize data integrator
    integrator = DataIntegrator()
    
    # Test 1: Load Keyboard Data
    print("\n1. 📝 Testing Keyboard Dataset...")
    try:
        keyboard_df = integrator.load_keyboard_data()
        if keyboard_df is not None and len(keyboard_df) > 0:
            print(f"   ✅ Keyboard data loaded successfully!")
            print(f"   📊 Dataset shape: {keyboard_df.shape}")
            print(f"   📈 Fatigue score range: {keyboard_df['fatigue_score'].min():.3f} - {keyboard_df['fatigue_score'].max():.3f}")
            print(f"   📋 Sample data:")
            print(keyboard_df.head(3).to_string(index=False))
        else:
            print("   ❌ Failed to load keyboard data")
    except Exception as e:
        print(f"   ❌ Error loading keyboard data: {e}")
    
    # Test 2: Load Mouse Data
    print("\n2. 🖱️  Testing Mouse Dataset...")
    try:
        mouse_df = integrator.load_mouse_data()
        if mouse_df is not None and len(mouse_df) > 0:
            print(f"   ✅ Mouse data loaded successfully!")
            print(f"   📊 Dataset shape: {mouse_df.shape}")
            print(f"   📈 Fatigue score range: {mouse_df['fatigue_score'].min():.3f} - {mouse_df['fatigue_score'].max():.3f}")
            print(f"   🎯 Activity types: {mouse_df['activity_type'].unique()}")
            print(f"   ⏱️  Session duration range: {mouse_df['session_duration'].min():.1f} - {mouse_df['session_duration'].max():.1f} minutes")
        else:
            print("   ❌ Failed to load mouse data")
    except Exception as e:
        print(f"   ❌ Error loading mouse data: {e}")
    
    # Test 3: Load Facial Data
    print("\n3. 👁️  Testing Facial Dataset...")
    try:
        facial_df = integrator.load_facial_data()
        if facial_df is not None and len(facial_df) > 0:
            print(f"   ✅ Facial data loaded successfully!")
            print(f"   📊 Dataset shape: {facial_df.shape}")
            print(f"   📈 Fatigue score range: {facial_df['fatigue_score'].min():.3f} - {facial_df['fatigue_score'].max():.3f}")
            print(f"   👁️  Eye states: {facial_df['eye_state'].unique() if 'eye_state' in facial_df.columns else 'N/A'}")
            print(f"   😴 Yawn states: {facial_df['yawn_state'].unique() if 'yawn_state' in facial_df.columns else 'N/A'}")
            print(f"   📂 Categories: {facial_df['category'].unique()}")
        else:
            print("   ❌ Failed to load facial data")
    except Exception as e:
        print(f"   ❌ Error loading facial data: {e}")
    
    # Test 4: Create Combined Dataset
    print("\n4. 🔗 Testing Dataset Integration...")
    try:
        # Create a comprehensive dataset by combining samples from all modalities
        combined_data = []
        
        # Sample from keyboard data
        if 'keyboard_df' in locals() and len(keyboard_df) > 0:
            for _, row in keyboard_df.head(10).iterrows():
                combined_data.append({
                    'typing_speed': row['typing_speed'],
                    'error_rate': row['error_rate'],
                    'pause_frequency': row['pause_frequency'],
                    'key_press_duration': row['key_press_duration'],
                    'movement_speed': 100,  # Default
                    'click_frequency': 5,   # Default
                    'eye_blink_rate': 20,   # Default
                    'eye_closure_duration': 0.2,  # Default
                    'speech_rate': 120,     # Default
                    'pitch_variation': 0.8, # Default
                    'volume': 0.9,          # Default
                    'clarity': 0.85,        # Default
                    'hour_of_day': 12,      # Default
                    'day_of_week': 1,       # Default
                    'fatigue_score': row['fatigue_score'],
                    'data_source': 'keyboard'
                })
        
        # Sample from mouse data
        if 'mouse_df' in locals() and len(mouse_df) > 0:
            for _, row in mouse_df.head(10).iterrows():
                combined_data.append({
                    'typing_speed': 45,     # Default
                    'error_rate': 5,        # Default
                    'pause_frequency': 3,   # Default
                    'key_press_duration': 120,  # Default
                    'movement_speed': row['movement_speed'],
                    'click_frequency': row['click_frequency'],
                    'eye_blink_rate': 20,   # Default
                    'eye_closure_duration': 0.2,  # Default
                    'speech_rate': 120,     # Default
                    'pitch_variation': 0.8, # Default
                    'volume': 0.9,          # Default
                    'clarity': 0.85,        # Default
                    'hour_of_day': 12,      # Default
                    'day_of_week': 1,       # Default
                    'fatigue_score': row['fatigue_score'],
                    'data_source': 'mouse'
                })
        
        # Sample from facial data
        if 'facial_df' in locals() and len(facial_df) > 0:
            for _, row in facial_df.head(10).iterrows():
                combined_data.append({
                    'typing_speed': 45,     # Default
                    'error_rate': 5,        # Default
                    'pause_frequency': 3,   # Default
                    'key_press_duration': 120,  # Default
                    'movement_speed': 100,  # Default
                    'click_frequency': 5,   # Default
                    'eye_blink_rate': row['eye_blink_rate'],
                    'eye_closure_duration': row['eye_closure_duration'],
                    'speech_rate': 120,     # Default
                    'pitch_variation': 0.8, # Default
                    'volume': 0.9,          # Default
                    'clarity': 0.85,        # Default
                    'hour_of_day': 12,      # Default
                    'day_of_week': 1,       # Default
                    'fatigue_score': row['fatigue_score'],
                    'data_source': 'facial'
                })
        
        if combined_data:
            combined_df = pd.DataFrame(combined_data)
            print(f"   ✅ Combined dataset created successfully!")
            print(f"   📊 Dataset shape: {combined_df.shape}")
            print(f"   📈 Fatigue score range: {combined_df['fatigue_score'].min():.3f} - {combined_df['fatigue_score'].max():.3f}")
            print(f"   📂 Data sources: {combined_df['data_source'].value_counts().to_dict()}")
            
            # Save combined dataset
            output_path = os.path.join(project_root, 'fatique', 'datasets', 'data', 'real_combined_dataset.csv')
            combined_df.to_csv(output_path, index=False)
            print(f"   💾 Saved combined dataset to: {output_path}")
            
        else:
            print("   ❌ No data available for combination")
            
    except Exception as e:
        print(f"   ❌ Error creating combined dataset: {e}")
    
    # Test 5: Dataset Statistics
    print("\n5. 📊 Dataset Statistics Summary...")
    try:
        total_samples = 0
        if 'keyboard_df' in locals():
            total_samples += len(keyboard_df)
        if 'mouse_df' in locals():
            total_samples += len(mouse_df)
        if 'facial_df' in locals():
            total_samples += len(facial_df)
        
        print(f"   📈 Total samples across all datasets: {total_samples}")
        print(f"   📝 Keyboard samples: {len(keyboard_df) if 'keyboard_df' in locals() else 0}")
        print(f"   🖱️  Mouse samples: {len(mouse_df) if 'mouse_df' in locals() else 0}")
        print(f"   👁️  Facial samples: {len(facial_df) if 'facial_df' in locals() else 0}")
        
        if 'combined_df' in locals():
            print(f"   🔗 Combined samples: {len(combined_df)}")
            
    except Exception as e:
        print(f"   ❌ Error calculating statistics: {e}")
    
    print("\n🎉 Dataset testing completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_real_datasets()
