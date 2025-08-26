"""
Dataset loader for mental fatigue detection system.
Handles loading and preprocessing of pre-existing datasets.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
import json
from django.conf import settings

class DatasetLoader:
    def __init__(self):
        self.dataset_path = os.path.join(settings.BASE_DIR, 'fatique', 'datasets', 'data')
        self.scaler = StandardScaler()
        
    def load_dataset(self, dataset_name='default'):
        """
        Load a pre-existing dataset.
        
        Args:
            dataset_name: Name of the dataset to load
            
        Returns:
            X: Feature matrix
            y: Target values (fatigue scores)
        """
        # Load the dataset
        data_path = os.path.join(self.dataset_path, f'{dataset_name}.csv')
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Dataset {dataset_name} not found at {data_path}")
        
        # Load the data
        df = pd.read_csv(data_path)
        
        # Separate features and target
        X = df.drop('fatigue_score', axis=1)
        y = df['fatigue_score']
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        return X, y
    
    def split_dataset(self, X, y, test_size=0.2, val_size=0.1):
        """
        Split dataset into train, validation, and test sets.
        
        Args:
            X: Feature matrix
            y: Target values
            test_size: Proportion of data to use for testing
            val_size: Proportion of training data to use for validation
            
        Returns:
            Dictionary containing train, validation, and test sets
        """
        # First split: separate test set
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Second split: separate validation set from training set
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val, y_train_val, 
            test_size=val_size/(1-test_size), 
            random_state=42
        )
        
        return {
            'train': (X_train, y_train),
            'val': (X_val, y_val),
            'test': (X_test, y_test)
        }
    
    def get_feature_names(self):
        """
        Get the names of features in the dataset.
        
        Returns:
            List of feature names
        """
        return [
            # Keyboard features
            'typing_speed', 'error_rate', 'pause_frequency', 'key_press_duration',
            # Mouse features
            'movement_speed', 'click_frequency',
            # Facial features
            'eye_blink_rate', 'eye_closure_duration',
            # Voice features
            'speech_rate', 'pitch_variation', 'volume', 'clarity',
            # Time-based features
            'hour_of_day', 'day_of_week'
        ]
    
    def get_dataset_info(self, dataset_name='default'):
        """
        Get information about the dataset.
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            Dictionary containing dataset information
        """
        info_path = os.path.join(self.dataset_path, f'{dataset_name}_info.json')
        
        if not os.path.exists(info_path):
            return {
                'name': dataset_name,
                'description': 'No description available',
                'num_samples': 0,
                'num_features': len(self.get_feature_names()),
                'feature_names': self.get_feature_names()
            }
        
        with open(info_path, 'r') as f:
            info = json.load(f)
        
        return info 