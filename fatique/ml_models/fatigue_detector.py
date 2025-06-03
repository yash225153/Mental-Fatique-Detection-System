"""
Fatigue detection model using machine learning.
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import os
import joblib
from django.conf import settings
from django.utils import timezone
from ..models import FatigueAnalysis, KeyboardMetrics, MouseMetrics, FacialMetrics, VoiceMetrics
from .data_preprocessor import DataPreprocessor
from ..datasets.dataset_loader import DatasetLoader
from ..datasets.data_integrator import DataIntegrator


class FatigueDetector:
    def __init__(self, model_path=None, use_real_data_model=True):
        """Initialize the fatigue detector."""
        self.model = None
        self.real_data_model = None
        self.scaler = None
        self.use_real_data_model = use_real_data_model
        self.preprocessor = DataPreprocessor()
        self.dataset_loader = DatasetLoader()
        self.data_integrator = DataIntegrator()

        # Try to load real data trained model first
        if use_real_data_model:
            self._load_real_data_model()

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        elif not self.real_data_model:
            self._build_model()

    def _load_real_data_model(self):
        """Load the model trained on real datasets."""
        try:
            model_dir = os.path.join(settings.BASE_DIR, 'ml_models', 'trained_models')
            model_path = os.path.join(model_dir, 'fatigue_model_real_data.joblib')
            scaler_path = os.path.join(model_dir, 'feature_scaler_real_data.joblib')

            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.real_data_model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                print("✅ Loaded real data trained model successfully!")
                return True
            else:
                print("❌ Real data trained model not found, falling back to neural network")
                return False
        except Exception as e:
            print(f"❌ Error loading real data model: {e}")
            return False

    def _build_model(self):
        """Build the neural network model."""
        model = Sequential([
            Dense(64, activation='relu', input_shape=(14,)),
            BatchNormalization(),
            Dropout(0.3),
            Dense(32, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            Dense(16, activation='relu'),
            BatchNormalization(),
            Dropout(0.1),
            Dense(1, activation='sigmoid')  # Output: fatigue score (0-1)
        ])

        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'mae']
        )

        self.model = model

    def train(self, X=None, y=None, dataset_name='default', epochs=100, batch_size=32, validation_split=0.2):
        """Train the model."""
        if self.model is None:
            self._build_model()

        if X is None or y is None:
            self.data_integrator.update_default_dataset()
            X, y = self.dataset_loader.load_dataset(dataset_name)
            splits = self.dataset_loader.split_dataset(X, y)
            X_train, y_train = splits['train']
            X_val, y_val = splits['val']

            callbacks = [
                EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
                ModelCheckpoint(
                    filepath=os.path.join(settings.BASE_DIR, 'fatique', 'ml_models', 'saved_models', 'best_model.h5'),
                    monitor='val_loss',
                    save_best_only=True
                )
            ]

            history = self.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=(X_val, y_val),
                callbacks=callbacks,
                verbose=1
            )
        else:
            history = self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                verbose=1
            )

        return history

    def predict(self, user=None, time_window=24, input_data=None):
        """Predict fatigue level for a user or input data."""

        # Use real data model if available
        if self.real_data_model and self.scaler:
            return self._predict_with_real_model(user, time_window, input_data)

        # Fallback to neural network model
        if self.model is None:
            raise ValueError("No model available for prediction")

        if input_data:
            # Use provided input data directly
            X = self._prepare_input_features(input_data)
        else:
            # Use user data from database
            self.preprocessor.fit(user=user, time_window=time_window)
            X = self.preprocessor.prepare_features(user, time_window)

        fatigue_score = float(self.model.predict(X)[0][0])

        if fatigue_score < 0.2:
            fatigue_level = 'very_low'
        elif fatigue_score < 0.4:
            fatigue_level = 'low'
        elif fatigue_score < 0.6:
            fatigue_level = 'moderate'
        elif fatigue_score < 0.8:
            fatigue_level = 'high'
        else:
            fatigue_level = 'severe'

        confidence = self._calculate_confidence(fatigue_score)
        contributing_factors = self._determine_contributing_factors(user, time_window, input_data)
        recommendations = self._generate_recommendations(fatigue_level, contributing_factors)

        if user:
            self._save_analysis(user, fatigue_score, fatigue_level, confidence, contributing_factors)

        return {
            'fatigue_score': fatigue_score * 100,
            'fatigue_level': fatigue_level,
            'confidence': confidence,
            'contributing_factors': contributing_factors,
            'recommendations': recommendations
        }

    def _predict_with_real_model(self, user=None, time_window=24, input_data=None):
        """Predict using the real data trained model."""
        try:
            # Prepare features for real data model
            if input_data:
                features = self._prepare_real_model_features(input_data)
            else:
                features = self._prepare_real_model_features_from_user(user, time_window)

            # Scale features
            features_scaled = self.scaler.transform([features])

            # Predict
            fatigue_score = float(self.real_data_model.predict(features_scaled)[0])

            # Ensure score is in valid range
            fatigue_score = max(0.0, min(1.0, fatigue_score))

            # Determine fatigue level
            if fatigue_score < 0.2:
                fatigue_level = 'very_low'
            elif fatigue_score < 0.4:
                fatigue_level = 'low'
            elif fatigue_score < 0.6:
                fatigue_level = 'moderate'
            elif fatigue_score < 0.8:
                fatigue_level = 'high'
            else:
                fatigue_level = 'severe'

            confidence = self._calculate_confidence(fatigue_score)
            contributing_factors = self._determine_contributing_factors(user, time_window, input_data)
            recommendations = self._generate_recommendations(fatigue_level, contributing_factors)

            if user:
                self._save_analysis(user, fatigue_score, fatigue_level, confidence, contributing_factors)

            return {
                'fatigue_score': fatigue_score * 100,
                'fatigue_level': fatigue_level,
                'confidence': confidence,
                'contributing_factors': contributing_factors,
                'recommendations': recommendations
            }

        except Exception as e:
            print(f"❌ Error in real model prediction: {e}")
            # Fallback to neural network
            return self.predict(user, time_window, input_data)

    def _prepare_real_model_features(self, input_data):
        """Prepare features for the real data model from input data."""
        # Feature order: typing_speed, error_rate, pause_frequency, key_press_duration,
        # movement_speed, click_frequency, eye_blink_rate, eye_closure_duration,
        # speech_rate, pitch_variation, volume, clarity, hour_of_day, day_of_week

        typing_data = input_data.get('typing_data', {})
        mouse_data = input_data.get('mouse_data', {})
        facial_data = input_data.get('facial_data', {})
        voice_data = input_data.get('voice_data', {})

        features = [
            typing_data.get('typingSpeed', 45),
            typing_data.get('errorRate', 5),
            typing_data.get('pauseFrequency', 3),
            typing_data.get('keyPressDuration', 120),
            mouse_data.get('movementSpeed', 120),
            mouse_data.get('clickFrequency', 8),
            facial_data.get('blinkRate', 20),
            facial_data.get('eyeClosure', 200) / 1000,  # Convert ms to seconds
            voice_data.get('speechRate', 120),
            voice_data.get('pitchVariation', 0.8),
            voice_data.get('volume', 0.9),
            voice_data.get('clarity', 0.85),
            timezone.now().hour,
            timezone.now().weekday() + 1
        ]

        return features

    def _prepare_real_model_features_from_user(self, user, time_window):
        """Prepare features for the real data model from user database data."""
        # Get latest metrics from database
        keyboard = KeyboardMetrics.objects.filter(user=user).order_by('-timestamp').first()
        mouse = MouseMetrics.objects.filter(user=user).order_by('-timestamp').first()
        facial = FacialMetrics.objects.filter(user=user).order_by('-timestamp').first()
        voice = VoiceMetrics.objects.filter(user=user).order_by('-timestamp').first()

        features = [
            keyboard.typing_speed if keyboard else 45,
            keyboard.error_rate if keyboard else 5,
            keyboard.pause_frequency if keyboard else 3,
            keyboard.key_press_duration if keyboard else 120,
            mouse.movement_speed if mouse else 120,
            mouse.click_frequency if mouse else 8,
            facial.eye_blink_rate if facial else 20,
            facial.eye_closure_duration / 1000 if facial else 0.2,  # Convert ms to seconds
            voice.speech_rate if voice else 120,
            voice.pitch_variation if voice else 0.8,
            voice.volume if voice else 0.9,
            voice.clarity if voice else 0.85,
            timezone.now().hour,
            timezone.now().weekday() + 1
        ]

        return features

    def _prepare_input_features(self, input_data):
        """Prepare input features for neural network model."""
        # This is a simplified version for the neural network
        features = self._prepare_real_model_features(input_data)
        return np.array([features])

    def _calculate_confidence(self, fatigue_score):
        """Calculate confidence in the prediction."""
        base_confidence = abs(fatigue_score - 0.5) * 2
        return min(max(base_confidence, 0.5), 0.95)

    def _determine_contributing_factors(self, user=None, time_window=24, input_data=None):
        """Determine the factors contributing to fatigue."""
        factors = {}

        if input_data:
            # Use input data directly
            typing_data = input_data.get('typing_data', {})
            mouse_data = input_data.get('mouse_data', {})
            facial_data = input_data.get('facial_data', {})

            # Analyze typing factors
            error_rate = typing_data.get('errorRate', 0)
            if error_rate > 10:
                factors['high_error_rate'] = {
                    'value': error_rate,
                    'severity': 'high' if error_rate > 15 else 'moderate'
                }

            pause_frequency = typing_data.get('pauseFrequency', 0)
            if pause_frequency > 5:
                factors['frequent_pauses'] = {
                    'value': pause_frequency,
                    'severity': 'high' if pause_frequency > 8 else 'moderate'
                }

            key_press_duration = typing_data.get('keyPressDuration', 0)
            if key_press_duration > 150:
                factors['slow_key_presses'] = {
                    'value': key_press_duration,
                    'severity': 'high' if key_press_duration > 200 else 'moderate'
                }

            # Analyze mouse factors
            movement_speed = mouse_data.get('movementSpeed', 100)
            if movement_speed < 100:
                factors['slow_mouse_movement'] = {
                    'value': movement_speed,
                    'severity': 'high' if movement_speed < 50 else 'moderate'
                }

            # Analyze facial factors
            blink_rate = facial_data.get('blinkRate', 20)
            if blink_rate < 10:
                factors['low_blink_rate'] = {
                    'value': blink_rate,
                    'severity': 'high' if blink_rate < 5 else 'moderate'
                }

            eye_closure = facial_data.get('eyeClosure', 200)
            if eye_closure > 300:
                factors['long_eye_closures'] = {
                    'value': eye_closure,
                    'severity': 'high' if eye_closure > 500 else 'moderate'
                }

        elif user:
            # Use database data
            keyboard = KeyboardMetrics.objects.filter(user=user).order_by('-timestamp').first()
            mouse = MouseMetrics.objects.filter(user=user).order_by('-timestamp').first()
            facial = FacialMetrics.objects.filter(user=user).order_by('-timestamp').first()

            if keyboard:
                if keyboard.error_rate > 10:
                    factors['high_error_rate'] = {
                        'value': keyboard.error_rate,
                        'severity': 'high' if keyboard.error_rate > 15 else 'moderate'
                    }
                if keyboard.pause_frequency > 5:
                    factors['frequent_pauses'] = {
                        'value': keyboard.pause_frequency,
                        'severity': 'high' if keyboard.pause_frequency > 8 else 'moderate'
                    }
                if keyboard.key_press_duration > 150:
                    factors['slow_key_presses'] = {
                        'value': keyboard.key_press_duration,
                        'severity': 'high' if keyboard.key_press_duration > 200 else 'moderate'
                    }

            if mouse:
                if mouse.movement_speed < 100:
                    factors['slow_mouse_movement'] = {
                        'value': mouse.movement_speed,
                        'severity': 'high' if mouse.movement_speed < 50 else 'moderate'
                    }

            if facial:
                if facial.eye_blink_rate < 10:
                    factors['low_blink_rate'] = {
                        'value': facial.eye_blink_rate,
                        'severity': 'high' if facial.eye_blink_rate < 5 else 'moderate'
                    }
                if facial.eye_closure_duration > 300:
                    factors['long_eye_closures'] = {
                        'value': facial.eye_closure_duration,
                        'severity': 'high' if facial.eye_closure_duration > 500 else 'moderate'
                    }

        # Time-based factors
        current_hour = timezone.now().hour
        if 14 <= current_hour <= 16:
            factors['afternoon_slump'] = {'severity': 'moderate'}
        elif current_hour >= 22 or current_hour <= 5:
            factors['late_hours'] = {'severity': 'high'}

        return factors

    def _generate_recommendations(self, fatigue_level, contributing_factors):
        """Generate recommendations based on fatigue level and contributing factors."""
        recommendations = []

        if fatigue_level in ['high', 'severe']:
            recommendations.append("Take a short break (15-20 minutes)")
            recommendations.append("Consider taking a power nap")
            recommendations.append("Stay hydrated and have a light snack")

        for factor, details in contributing_factors.items():
            if factor == 'high_error_rate':
                recommendations.append("Take a short break to refresh your focus")
            elif factor == 'frequent_pauses':
                recommendations.append("Consider taking a longer break to recover")
            elif factor == 'slow_key_presses':
                recommendations.append("Stretch your hands and fingers")
            elif factor == 'slow_mouse_movement':
                recommendations.append("Take a short walk to improve circulation")
            elif factor == 'low_blink_rate':
                recommendations.append("Practice the 20-20-20 rule")
            elif factor == 'long_eye_closures':
                recommendations.append("Take a short break to rest your eyes")
            elif factor == 'afternoon_slump':
                recommendations.append("Consider a short walk or light exercise")
            elif factor == 'late_hours':
                recommendations.append("Consider ending your work session soon")

        return recommendations

    def _save_analysis(self, user, fatigue_score, fatigue_level, confidence, contributing_factors, recommendations):
        """Save fatigue analysis to the database."""
        FatigueAnalysis.objects.create(
            user=user,
            fatigue_score=fatigue_score * 100,
            fatigue_level=fatigue_level,
            confidence=confidence,
            contributing_factors=contributing_factors,
            timestamp=timezone.now()
        )

    def save_model(self, model_path):
        """Save the model to a file."""
        if self.model is None:
            raise ValueError("No model to save")

        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        self.model.save(model_path)

        preprocessor_path = os.path.join(os.path.dirname(model_path), 'fatigue_preprocessor.joblib')
        joblib.dump(self.preprocessor, preprocessor_path)

    def load_model(self, model_path):
        """Load the model from a file."""
        if not os.path.exists(model_path):
            raise ValueError(f"Model file not found: {model_path}")

        self.model = load_model(model_path)

        preprocessor_path = os.path.join(os.path.dirname(model_path), 'fatigue_preprocessor.joblib')
        if os.path.exists(preprocessor_path):
            self.preprocessor = joblib.load(preprocessor_path)
        else:
            self.preprocessor = DataPreprocessor()

    def evaluate(self, X_test=None, y_test=None, dataset_name='default'):
        """Evaluate the model on test data."""
        if self.model is None:
            raise ValueError("Model not trained or loaded")

        if X_test is None or y_test is None:
            X, y = self.dataset_loader.load_dataset(dataset_name)
            splits = self.dataset_loader.split_dataset(X, y)
            X_test, y_test = splits['test']

        y_pred_prob = self.model.predict(X_test)
        y_pred = (y_pred_prob > 0.5).astype(int)

        return {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
