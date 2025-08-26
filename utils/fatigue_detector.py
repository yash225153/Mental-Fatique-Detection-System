import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from sklearn.preprocessing import StandardScaler
from data_collection.models import UserBehavior, FatigueLevel
import json

class FatigueDetector:
    def __init__(self):
        self.model = self._build_model()
        self.scaler = StandardScaler()
        self.is_trained = False

    def _build_model(self):
        model = Sequential([
            LSTM(128, input_shape=(10, 6), return_sequences=True),
            Dropout(0.2),
            LSTM(64),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def prepare_data(self, user):
        # Get last 10 minutes of behavior data
        behaviors = UserBehavior.objects.filter(
            user=user
        ).order_by('-timestamp')[:10]
        
        if len(behaviors) < 10:
            return None
        
        # Prepare features
        X = []
        for behavior in behaviors:
            # Basic features
            features = [
                behavior.typing_speed if behavior.typing_speed else 0,
                behavior.mouse_movement_count if behavior.mouse_movement_count else 0
            ]
            
            # Face features
            if behavior.face_detection_data:
                face_data = json.loads(behavior.face_detection_data)
                features.extend([
                    face_data.get('eye_aspect_ratio', 0),
                    face_data.get('mouth_aspect_ratio', 0)
                ])
            else:
                features.extend([0, 0])
            
            # Voice features
            if behavior.voice_analysis_data:
                voice_data = json.loads(behavior.voice_analysis_data)
                features.extend([
                    voice_data.get('pitch_mean', 0),
                    voice_data.get('energy_mean', 0)
                ])
            else:
                features.extend([0, 0])
            
            X.append(features)
        
        X = np.array(X)
        
        # Scale features
        if not self.is_trained:
            self.scaler.fit(X)
            self.is_trained = True
        
        X = self.scaler.transform(X)
        X = X.reshape(1, 10, 6)  # Reshape for LSTM
        
        return X

    def predict_fatigue(self, user):
        X = self.prepare_data(user)
        if X is None:
            return None, None
        
        # Make prediction
        fatigue_score = self.model.predict(X)[0][0]
        
        # Calculate confidence based on data availability
        behaviors = UserBehavior.objects.filter(user=user).order_by('-timestamp')[:10]
        data_sources = sum([
            1 if b.typing_speed else 0,
            1 if b.mouse_movement_count else 0,
            1 if b.face_detection_data else 0,
            1 if b.voice_analysis_data else 0
        ] for b in behaviors)
        confidence = min(1.0, data_sources / (4 * len(behaviors)))
        
        # Save prediction
        FatigueLevel.objects.create(
            user=user,
            fatigue_score=fatigue_score * 100,
            confidence=confidence * 100,
            data_source='combined'
        )
        
        return fatigue_score, confidence

    def train_model(self, X_train, y_train):
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_train_scaled = X_train_scaled.reshape(-1, 10, 6)
        
        # Train model
        self.model.fit(
            X_train_scaled, 
            y_train, 
            epochs=20, 
            batch_size=32,
            validation_split=0.2
        )
        self.is_trained = True 