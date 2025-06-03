"""
Data preprocessing module for machine learning models.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from django.utils import timezone
from datetime import timedelta
from ..models import (
    KeyboardMetrics,
    MouseMetrics,
    FacialMetrics,
    VoiceMetrics
)

class DataPreprocessor:
    def __init__(self):
        self.keyboard_scaler = StandardScaler()
        self.mouse_scaler = StandardScaler()
        self.facial_scaler = StandardScaler()
        self.voice_scaler = StandardScaler()
        self.is_fitted = False
    
    def fit(self, user=None, time_window=None):
        """
        Fit the scalers on historical data.
        
        Args:
            user: Optional user to filter data by
            time_window: Optional time window to filter data by (in hours)
        """
        # Get data from the database
        keyboard_data = self._get_keyboard_data(user, time_window)
        mouse_data = self._get_mouse_data(user, time_window)
        facial_data = self._get_facial_data(user, time_window)
        voice_data = self._get_voice_data(user, time_window)
        
        # Fit scalers if we have enough data
        if len(keyboard_data) > 0:
            self.keyboard_scaler.fit(keyboard_data)
        
        if len(mouse_data) > 0:
            self.mouse_scaler.fit(mouse_data)
        
        if len(facial_data) > 0:
            self.facial_scaler.fit(facial_data)
        
        if len(voice_data) > 0:
            self.voice_scaler.fit(voice_data)
        
        self.is_fitted = True
    
    def transform(self, keyboard_metrics=None, mouse_metrics=None, facial_metrics=None, voice_metrics=None):
        """
        Transform metrics using fitted scalers.
        
        Args:
            keyboard_metrics: Dictionary of keyboard metrics
            mouse_metrics: Dictionary of mouse metrics
            facial_metrics: Dictionary of facial metrics
            voice_metrics: Dictionary of voice metrics
            
        Returns:
            Dictionary of transformed metrics
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")
        
        transformed_data = {}
        
        # Transform keyboard metrics
        if keyboard_metrics is not None:
            keyboard_array = np.array([
                keyboard_metrics.get('typing_speed', 0),
                keyboard_metrics.get('error_rate', 0),
                keyboard_metrics.get('pause_frequency', 0),
                keyboard_metrics.get('key_press_duration', 0)
            ]).reshape(1, -1)
            
            transformed_data['keyboard'] = self.keyboard_scaler.transform(keyboard_array)[0]
        
        # Transform mouse metrics
        if mouse_metrics is not None:
            mouse_array = np.array([
                mouse_metrics.get('movement_speed', 0),
                mouse_metrics.get('click_frequency', 0)
            ]).reshape(1, -1)
            
            transformed_data['mouse'] = self.mouse_scaler.transform(mouse_array)[0]
        
        # Transform facial metrics
        if facial_metrics is not None:
            facial_array = np.array([
                facial_metrics.get('eye_blink_rate', 0),
                facial_metrics.get('eye_closure_duration', 0)
            ]).reshape(1, -1)
            
            transformed_data['facial'] = self.facial_scaler.transform(facial_array)[0]
        
        # Transform voice metrics
        if voice_metrics is not None:
            voice_array = np.array([
                voice_metrics.get('speech_rate', 0),
                voice_metrics.get('pitch_variation', 0),
                voice_metrics.get('volume', 0),
                voice_metrics.get('clarity', 0)
            ]).reshape(1, -1)
            
            transformed_data['voice'] = self.voice_scaler.transform(voice_array)[0]
        
        return transformed_data
    
    def prepare_features(self, user, time_window=24):
        """
        Prepare features for model training or prediction.
        
        Args:
            user: User to get data for
            time_window: Time window in hours
            
        Returns:
            Feature matrix X
        """
        # Get the latest metrics for each modality
        keyboard_metrics = self._get_latest_keyboard_metrics(user, time_window)
        mouse_metrics = self._get_latest_mouse_metrics(user, time_window)
        facial_metrics = self._get_latest_facial_metrics(user, time_window)
        voice_metrics = self._get_latest_voice_metrics(user, time_window)
        
        # Transform metrics
        transformed_data = self.transform(
            keyboard_metrics=keyboard_metrics,
            mouse_metrics=mouse_metrics,
            facial_metrics=facial_metrics,
            voice_metrics=voice_metrics
        )
        
        # Combine all features
        features = []
        
        if 'keyboard' in transformed_data:
            features.extend(transformed_data['keyboard'])
        else:
            features.extend([0, 0, 0, 0])  # Placeholder for missing keyboard data
        
        if 'mouse' in transformed_data:
            features.extend(transformed_data['mouse'])
        else:
            features.extend([0, 0])  # Placeholder for missing mouse data
        
        if 'facial' in transformed_data:
            features.extend(transformed_data['facial'])
        else:
            features.extend([0, 0])  # Placeholder for missing facial data
        
        if 'voice' in transformed_data:
            features.extend(transformed_data['voice'])
        else:
            features.extend([0, 0, 0, 0])  # Placeholder for missing voice data
        
        # Add time-based features
        current_time = timezone.now()
        features.append(current_time.hour / 24.0)  # Hour of day (normalized)
        features.append(current_time.weekday() / 6.0)  # Day of week (normalized)
        
        return np.array(features).reshape(1, -1)
    
    def _get_keyboard_data(self, user=None, time_window=None):
        """Get keyboard data as a numpy array."""
        query = KeyboardMetrics.objects.all()
        
        if user is not None:
            query = query.filter(user=user)
        
        if time_window is not None:
            cutoff_time = timezone.now() - timedelta(hours=time_window)
            query = query.filter(timestamp__gte=cutoff_time)
        
        metrics = query.values_list('typing_speed', 'error_rate', 'pause_frequency', 'key_press_duration')
        return np.array(list(metrics))
    
    def _get_mouse_data(self, user=None, time_window=None):
        """Get mouse data as a numpy array."""
        query = MouseMetrics.objects.all()
        
        if user is not None:
            query = query.filter(user=user)
        
        if time_window is not None:
            cutoff_time = timezone.now() - timedelta(hours=time_window)
            query = query.filter(timestamp__gte=cutoff_time)
        
        metrics = query.values_list('movement_speed', 'click_frequency')
        return np.array(list(metrics))
    
    def _get_facial_data(self, user=None, time_window=None):
        """Get facial data as a numpy array."""
        query = FacialMetrics.objects.all()
        
        if user is not None:
            query = query.filter(user=user)
        
        if time_window is not None:
            cutoff_time = timezone.now() - timedelta(hours=time_window)
            query = query.filter(timestamp__gte=cutoff_time)
        
        metrics = query.values_list('eye_blink_rate', 'eye_closure_duration')
        return np.array(list(metrics))
    
    def _get_voice_data(self, user=None, time_window=None):
        """Get voice data as a numpy array."""
        query = VoiceMetrics.objects.all()
        
        if user is not None:
            query = query.filter(user=user)
        
        if time_window is not None:
            cutoff_time = timezone.now() - timedelta(hours=time_window)
            query = query.filter(timestamp__gte=cutoff_time)
        
        metrics = query.values_list('speech_rate', 'pitch_variation', 'volume', 'clarity')
        return np.array(list(metrics))
    
    def _get_latest_keyboard_metrics(self, user, time_window=24):
        """Get the latest keyboard metrics for a user."""
        cutoff_time = timezone.now() - timedelta(hours=time_window)
        latest = KeyboardMetrics.objects.filter(
            user=user,
            timestamp__gte=cutoff_time
        ).order_by('-timestamp').first()
        
        if latest:
            return {
                'typing_speed': latest.typing_speed,
                'error_rate': latest.error_rate,
                'pause_frequency': latest.pause_frequency,
                'key_press_duration': latest.key_press_duration
            }
        
        return None
    
    def _get_latest_mouse_metrics(self, user, time_window=24):
        """Get the latest mouse metrics for a user."""
        cutoff_time = timezone.now() - timedelta(hours=time_window)
        latest = MouseMetrics.objects.filter(
            user=user,
            timestamp__gte=cutoff_time
        ).order_by('-timestamp').first()
        
        if latest:
            return {
                'movement_speed': latest.movement_speed,
                'click_frequency': latest.click_frequency
            }
        
        return None
    
    def _get_latest_facial_metrics(self, user, time_window=24):
        """Get the latest facial metrics for a user."""
        cutoff_time = timezone.now() - timedelta(hours=time_window)
        latest = FacialMetrics.objects.filter(
            user=user,
            timestamp__gte=cutoff_time
        ).order_by('-timestamp').first()
        
        if latest:
            return {
                'eye_blink_rate': latest.eye_blink_rate,
                'eye_closure_duration': latest.eye_closure_duration
            }
        
        return None
    
    def _get_latest_voice_metrics(self, user, time_window=24):
        """Get the latest voice metrics for a user."""
        cutoff_time = timezone.now() - timedelta(hours=time_window)
        latest = VoiceMetrics.objects.filter(
            user=user,
            timestamp__gte=cutoff_time
        ).order_by('-timestamp').first()
        
        if latest:
            return {
                'speech_rate': latest.speech_rate,
                'pitch_variation': latest.pitch_variation,
                'volume': latest.volume,
                'clarity': latest.clarity
            }
        
        return None
