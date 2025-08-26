#!/usr/bin/env python3
"""
Enhanced ML training script using real datasets for the Mental Fatigue Detector.
This script trains the fatigue detection models using the provided real datasets.
"""

import os
import sys
import django
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental_fatique.settings')
django.setup()

from fatique.datasets.data_integrator import DataIntegrator

def prepare_training_data():
    """Prepare comprehensive training data from all real datasets."""
    
    print("📊 Preparing Training Data from Real Datasets...")
    print("=" * 50)
    
    integrator = DataIntegrator()
    
    # Load all datasets
    keyboard_df = integrator.load_keyboard_data()
    mouse_df = integrator.load_mouse_data()
    facial_df = integrator.load_facial_data()
    
    # Create comprehensive training samples
    training_data = []
    
    # Process keyboard data (100 samples)
    print(f"Processing {len(keyboard_df)} keyboard samples...")
    for _, row in keyboard_df.iterrows():
        training_data.append({
            'typing_speed': row['typing_speed'],
            'error_rate': row['error_rate'],
            'pause_frequency': row['pause_frequency'],
            'key_press_duration': row['key_press_duration'],
            'movement_speed': np.random.normal(120, 30),  # Simulated
            'click_frequency': np.random.normal(8, 3),    # Simulated
            'eye_blink_rate': np.random.normal(20, 5),    # Simulated
            'eye_closure_duration': np.random.normal(0.2, 0.05),  # Simulated
            'speech_rate': np.random.normal(120, 20),     # Default
            'pitch_variation': np.random.normal(0.8, 0.2), # Default
            'volume': np.random.normal(0.9, 0.1),         # Default
            'clarity': np.random.normal(0.85, 0.1),       # Default
            'hour_of_day': np.random.randint(8, 22),      # Work hours
            'day_of_week': np.random.randint(1, 8),       # 1-7
            'fatigue_score': row['fatigue_score'],
            'data_source': 'keyboard'
        })
    
    # Process mouse data (22 samples, expand with variations)
    print(f"Processing {len(mouse_df)} mouse samples...")
    for _, row in mouse_df.iterrows():
        # Create multiple variations of each mouse session
        for variation in range(5):  # 5 variations per session
            training_data.append({
                'typing_speed': np.random.normal(45, 10),  # Simulated
                'error_rate': np.random.normal(5, 2),      # Simulated
                'pause_frequency': np.random.normal(3, 1), # Simulated
                'key_press_duration': np.random.normal(120, 20),  # Simulated
                'movement_speed': row['movement_speed'] + np.random.normal(0, 10),
                'click_frequency': row['click_frequency'] + np.random.normal(0, 1),
                'eye_blink_rate': np.random.normal(20, 5),    # Simulated
                'eye_closure_duration': np.random.normal(0.2, 0.05),  # Simulated
                'speech_rate': np.random.normal(120, 20),     # Default
                'pitch_variation': np.random.normal(0.8, 0.2), # Default
                'volume': np.random.normal(0.9, 0.1),         # Default
                'clarity': np.random.normal(0.85, 0.1),       # Default
                'hour_of_day': np.random.randint(8, 22),      # Work hours
                'day_of_week': np.random.randint(1, 8),       # 1-7
                'fatigue_score': row['fatigue_score'] + np.random.normal(0, 0.05),
                'data_source': 'mouse'
            })
    
    # Process facial data (sample 200 from 2900 to balance dataset)
    print(f"Processing sample of {min(200, len(facial_df))} facial samples...")
    facial_sample = facial_df.sample(n=min(200, len(facial_df)), random_state=42)
    for _, row in facial_sample.iterrows():
        training_data.append({
            'typing_speed': np.random.normal(45, 10),  # Simulated
            'error_rate': np.random.normal(5, 2),      # Simulated
            'pause_frequency': np.random.normal(3, 1), # Simulated
            'key_press_duration': np.random.normal(120, 20),  # Simulated
            'movement_speed': np.random.normal(120, 30),  # Simulated
            'click_frequency': np.random.normal(8, 3),    # Simulated
            'eye_blink_rate': row['eye_blink_rate'],
            'eye_closure_duration': row['eye_closure_duration'],
            'speech_rate': np.random.normal(120, 20),     # Default
            'pitch_variation': np.random.normal(0.8, 0.2), # Default
            'volume': np.random.normal(0.9, 0.1),         # Default
            'clarity': np.random.normal(0.85, 0.1),       # Default
            'hour_of_day': np.random.randint(8, 22),      # Work hours
            'day_of_week': np.random.randint(1, 8),       # 1-7
            'fatigue_score': row['fatigue_score'],
            'data_source': 'facial'
        })
    
    # Convert to DataFrame
    training_df = pd.DataFrame(training_data)
    
    # Clean and validate data
    training_df = training_df.dropna()
    training_df['fatigue_score'] = training_df['fatigue_score'].clip(0, 1)
    
    print(f"✅ Prepared {len(training_df)} training samples")
    print(f"📊 Data sources: {training_df['data_source'].value_counts().to_dict()}")
    print(f"📈 Fatigue score range: {training_df['fatigue_score'].min():.3f} - {training_df['fatigue_score'].max():.3f}")
    
    return training_df

def train_fatigue_model(training_df):
    """Train the fatigue detection model using real data."""
    
    print("\n🤖 Training Fatigue Detection Model...")
    print("=" * 50)
    
    # Prepare features and target
    feature_columns = [
        'typing_speed', 'error_rate', 'pause_frequency', 'key_press_duration',
        'movement_speed', 'click_frequency', 'eye_blink_rate', 'eye_closure_duration',
        'speech_rate', 'pitch_variation', 'volume', 'clarity',
        'hour_of_day', 'day_of_week'
    ]
    
    X = training_df[feature_columns]
    y = training_df['fatigue_score']
    
    print(f"📊 Feature matrix shape: {X.shape}")
    print(f"🎯 Target vector shape: {y.shape}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=None
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    print("🌲 Training Random Forest model...")
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    rf_model.fit(X_train_scaled, y_train)
    
    # Evaluate model
    train_pred = rf_model.predict(X_train_scaled)
    test_pred = rf_model.predict(X_test_scaled)
    
    train_mse = mean_squared_error(y_train, train_pred)
    test_mse = mean_squared_error(y_test, test_pred)
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)
    
    print(f"📈 Training Results:")
    print(f"   - Training MSE: {train_mse:.4f}")
    print(f"   - Test MSE: {test_mse:.4f}")
    print(f"   - Training R²: {train_r2:.4f}")
    print(f"   - Test R²: {test_r2:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n🔍 Top 5 Most Important Features:")
    for _, row in feature_importance.head().iterrows():
        print(f"   - {row['feature']}: {row['importance']:.4f}")
    
    # Save model and scaler
    model_dir = os.path.join(project_root, 'ml_models', 'trained_models')
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'fatigue_model_real_data.joblib')
    scaler_path = os.path.join(model_dir, 'feature_scaler_real_data.joblib')
    
    joblib.dump(rf_model, model_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"💾 Model saved to: {model_path}")
    print(f"💾 Scaler saved to: {scaler_path}")
    
    return rf_model, scaler, feature_importance

def test_model_predictions(model, scaler):
    """Test the trained model with sample predictions."""
    
    print("\n🧪 Testing Model Predictions...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            'name': 'Low Fatigue (Morning)',
            'data': [60, 2, 1, 100, 150, 10, 15, 0.15, 130, 0.9, 0.95, 0.9, 9, 2]
        },
        {
            'name': 'Medium Fatigue (Afternoon)',
            'data': [45, 5, 3, 120, 120, 8, 20, 0.2, 120, 0.8, 0.9, 0.85, 14, 3]
        },
        {
            'name': 'High Fatigue (Evening)',
            'data': [30, 8, 5, 150, 80, 5, 30, 0.4, 100, 0.6, 0.8, 0.7, 20, 5]
        }
    ]
    
    for test_case in test_cases:
        data_scaled = scaler.transform([test_case['data']])
        prediction = model.predict(data_scaled)[0]
        print(f"   {test_case['name']}: {prediction:.3f}")
    
    print("✅ Model testing completed!")

def main():
    """Main training pipeline."""
    
    print("🚀 Starting Enhanced ML Training with Real Datasets")
    print("=" * 60)
    
    try:
        # Prepare training data
        training_df = prepare_training_data()
        
        # Save training dataset
        dataset_path = os.path.join(project_root, 'fatique', 'datasets', 'data', 'enhanced_training_dataset.csv')
        training_df.to_csv(dataset_path, index=False)
        print(f"💾 Training dataset saved to: {dataset_path}")
        
        # Train model
        model, scaler, feature_importance = train_fatigue_model(training_df)
        
        # Test model
        test_model_predictions(model, scaler)
        
        print("\n🎉 Training completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during training: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
