"""
Enhanced Data integrator for combining facial, mouse, and keyboard datasets.
Processes real datasets provided by the user.
"""

import os
import pandas as pd
import numpy as np
import glob
import json
from datetime import datetime
from django.conf import settings
from .dataset_loader import DatasetLoader

# Optional imports for image processing
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class DataIntegrator:
    def __init__(self):
        self.base_dir = settings.BASE_DIR
        self.facial_dir = os.path.join(self.base_dir, 'facial_data')
        self.mouse_dir = os.path.join(self.base_dir, 'mouse_data')
        self.keyboard_dir = os.path.join(self.base_dir, 'keyboard_data')
        self.dataset_loader = DatasetLoader()

        # Dataset statistics for normalization
        self.dataset_stats = {
            'keyboard': {
                'typing_speed': {'min': 18.8, 'max': 63.52, 'mean': 44.5, 'std': 9.8},
                'error_rate': {'min': 1.16, 'max': 10.44, 'mean': 5.1, 'std': 2.1},
                'pause_frequency': {'min': 0.0, 'max': 6.85, 'mean': 3.0, 'std': 1.2},
                'key_press_duration': {'min': 56.28, 'max': 185.69, 'mean': 122.4, 'std': 25.8}
            },
            'facial': {
                'eye_states': ['Open', 'Closed'],
                'fatigue_indicators': ['no_yawn', 'yawn'],
                'total_samples': {'train': 0, 'test': 0}
            },
            'mouse': {
                'activity_levels': ['Browsing_Normal', 'Stressed', 'Rest'],
                'session_durations': {'min': 3, 'max': 84, 'mean': 25, 'std': 18}
            }
        }

    def load_keyboard_data(self):
        """Load and preprocess real keyboard data from CSV file."""
        keyboard_file = os.path.join(self.keyboard_dir, 'keystroke_dynamics_dataset.csv')

        try:
            if os.path.exists(keyboard_file):
                df = pd.read_csv(keyboard_file)
                print(f"✅ Loaded keyboard dataset with {len(df)} samples")

                # Calculate fatigue scores based on typing patterns
                fatigue_scores = []
                for _, row in df.iterrows():
                    # Calculate fatigue based on multiple factors
                    speed_factor = max(0, (50 - row['typing_speed']) / 50)  # Lower speed = higher fatigue
                    error_factor = min(1, row['error_rate'] / 10)  # Higher errors = higher fatigue
                    pause_factor = min(1, row['pause_frequency'] / 7)  # More pauses = higher fatigue
                    duration_factor = min(1, (row['key_press_duration'] - 80) / 120)  # Longer press = higher fatigue

                    # Weighted combination (0-1 scale)
                    fatigue_score = (speed_factor * 0.3 + error_factor * 0.3 +
                                   pause_factor * 0.2 + duration_factor * 0.2)
                    fatigue_scores.append(min(max(fatigue_score, 0), 1))

                df['fatigue_score'] = fatigue_scores

                # Return the full dataset for training
                return df
            else:
                print(f"❌ Keyboard data file not found: {keyboard_file}")
                return self._get_default_keyboard_data()

        except Exception as e:
            print(f"❌ Error loading keyboard data: {e}")
            return self._get_default_keyboard_data()

    def _get_default_keyboard_data(self):
        """Return default keyboard data if real data is not available."""
        return pd.DataFrame({
            'typing_speed': [43.96],
            'error_rate': [5.04],
            'pause_frequency': [3.07],
            'key_press_duration': [123.20],
            'fatigue_score': [0.5]
        })

    def load_mouse_data(self):
        """Load and preprocess real mouse data from IOGraphica images."""
        try:
            mouse_data = []

            # Process training data
            train_dir = os.path.join(self.mouse_dir, 'Train')
            if os.path.exists(train_dir):
                for activity_type in ['Browsing_Normal', 'Stressed', 'Rest']:
                    activity_dir = os.path.join(train_dir, activity_type)
                    if os.path.exists(activity_dir):
                        png_files = glob.glob(os.path.join(activity_dir, '*.png'))

                        for png_file in png_files:
                            # Extract session duration from filename
                            filename = os.path.basename(png_file)
                            duration = self._extract_duration_from_filename(filename)

                            # Calculate fatigue score based on activity type and duration
                            if activity_type == 'Browsing_Normal':
                                base_fatigue = 0.3
                            elif activity_type == 'Stressed':
                                base_fatigue = 0.8
                            else:  # Rest
                                base_fatigue = 0.1

                            # Adjust fatigue based on session duration (longer sessions = more fatigue)
                            duration_factor = min(1.0, duration / 60)  # Normalize to 1 hour
                            fatigue_score = min(1.0, base_fatigue + (duration_factor * 0.3))

                            mouse_data.append({
                                'activity_type': activity_type,
                                'session_duration': duration,
                                'movement_speed': self._estimate_movement_speed(activity_type),
                                'click_frequency': self._estimate_click_frequency(activity_type),
                                'fatigue_score': fatigue_score,
                                'filename': filename
                            })

                print(f"✅ Loaded mouse dataset with {len(mouse_data)} sessions")
                return pd.DataFrame(mouse_data)
            else:
                print(f"❌ Mouse data directory not found: {train_dir}")
                return self._get_default_mouse_data()

        except Exception as e:
            print(f"❌ Error loading mouse data: {e}")
            return self._get_default_mouse_data()

    def _extract_duration_from_filename(self, filename):
        """Extract session duration in minutes from IOGraphica filename."""
        try:
            # Parse filenames like "IOGraphica - 12 minutes (from 22-34 to 22-47).png"
            if 'minute' in filename:
                parts = filename.split(' ')
                for i, part in enumerate(parts):
                    if 'minute' in part and i > 0:
                        duration_str = parts[i-1]
                        if duration_str.replace('.', '').isdigit():
                            return float(duration_str)
            elif 'hour' in filename:
                # Handle hour-based durations
                parts = filename.split(' ')
                for i, part in enumerate(parts):
                    if 'hour' in part and i > 0:
                        duration_str = parts[i-1]
                        if duration_str.replace('.', '').isdigit():
                            return float(duration_str) * 60  # Convert to minutes
            return 15  # Default duration
        except:
            return 15  # Default duration

    def _estimate_movement_speed(self, activity_type):
        """Estimate mouse movement speed based on activity type."""
        if activity_type == 'Browsing_Normal':
            return np.random.normal(120, 20)
        elif activity_type == 'Stressed':
            return np.random.normal(180, 30)  # Faster, more erratic
        else:  # Rest
            return np.random.normal(60, 15)   # Slower

    def _estimate_click_frequency(self, activity_type):
        """Estimate click frequency based on activity type."""
        if activity_type == 'Browsing_Normal':
            return np.random.normal(8, 2)
        elif activity_type == 'Stressed':
            return np.random.normal(15, 4)  # More clicks when stressed
        else:  # Rest
            return np.random.normal(3, 1)   # Fewer clicks during rest

    def _get_default_mouse_data(self):
        """Return default mouse data if real data is not available."""
        return pd.DataFrame({
            'activity_type': ['Browsing_Normal'],
            'session_duration': [15],
            'movement_speed': [100],
            'click_frequency': [5],
            'fatigue_score': [0.5],
            'filename': ['default']
        })

    def load_facial_data(self):
        """Load and preprocess real facial data from image datasets."""
        try:
            facial_data = []

            # Process training data
            train_dir = os.path.join(self.facial_dir, 'train')
            test_dir = os.path.join(self.facial_dir, 'test')

            for data_split, base_dir in [('train', train_dir), ('test', test_dir)]:
                if os.path.exists(base_dir):
                    # Process eye state data (Open/Closed)
                    for eye_state in ['Open', 'Closed']:
                        eye_dir = os.path.join(base_dir, eye_state)
                        if os.path.exists(eye_dir):
                            image_files = glob.glob(os.path.join(eye_dir, '*.jpg'))

                            for img_file in image_files:
                                # Calculate fatigue score based on eye state
                                eye_fatigue = 0.8 if eye_state == 'Closed' else 0.2

                                facial_data.append({
                                    'data_split': data_split,
                                    'eye_state': eye_state,
                                    'eye_blink_rate': self._estimate_blink_rate(eye_state),
                                    'eye_closure_duration': self._estimate_closure_duration(eye_state),
                                    'fatigue_score': eye_fatigue,
                                    'filename': os.path.basename(img_file),
                                    'category': 'eye_state'
                                })

                    # Process yawn data (yawn/no_yawn)
                    for yawn_state in ['yawn', 'no_yawn']:
                        yawn_dir = os.path.join(base_dir, yawn_state)
                        if os.path.exists(yawn_dir):
                            image_files = glob.glob(os.path.join(yawn_dir, '*.jpg'))

                            for img_file in image_files:
                                # Calculate fatigue score based on yawn state
                                yawn_fatigue = 0.9 if yawn_state == 'yawn' else 0.3

                                facial_data.append({
                                    'data_split': data_split,
                                    'yawn_state': yawn_state,
                                    'eye_blink_rate': self._estimate_blink_rate_from_yawn(yawn_state),
                                    'eye_closure_duration': self._estimate_closure_from_yawn(yawn_state),
                                    'fatigue_score': yawn_fatigue,
                                    'filename': os.path.basename(img_file),
                                    'category': 'yawn_detection'
                                })

            if facial_data:
                df = pd.DataFrame(facial_data)
                print(f"✅ Loaded facial dataset with {len(df)} images")
                print(f"   - Training samples: {len(df[df['data_split'] == 'train'])}")
                print(f"   - Test samples: {len(df[df['data_split'] == 'test'])}")
                return df
            else:
                print("❌ No facial data found")
                return self._get_default_facial_data()

        except Exception as e:
            print(f"❌ Error loading facial data: {e}")
            return self._get_default_facial_data()

    def _estimate_blink_rate(self, eye_state):
        """Estimate blink rate based on eye state."""
        if eye_state == 'Closed':
            return np.random.normal(25, 5)  # Higher blink rate when tired
        else:
            return np.random.normal(15, 3)  # Normal blink rate

    def _estimate_closure_duration(self, eye_state):
        """Estimate eye closure duration based on eye state."""
        if eye_state == 'Closed':
            return np.random.normal(0.4, 0.1)  # Longer closure when tired
        else:
            return np.random.normal(0.15, 0.05)  # Normal closure duration

    def _estimate_blink_rate_from_yawn(self, yawn_state):
        """Estimate blink rate based on yawn state."""
        if yawn_state == 'yawn':
            return np.random.normal(30, 6)  # Higher blink rate when yawning
        else:
            return np.random.normal(18, 4)  # Normal blink rate

    def _estimate_closure_from_yawn(self, yawn_state):
        """Estimate eye closure duration based on yawn state."""
        if yawn_state == 'yawn':
            return np.random.normal(0.5, 0.15)  # Longer closure when yawning
        else:
            return np.random.normal(0.2, 0.08)  # Normal closure duration

    def _get_default_facial_data(self):
        """Return default facial data if real data is not available."""
        return pd.DataFrame({
            'data_split': ['train'],
            'eye_state': ['Open'],
            'yawn_state': ['no_yawn'],
            'eye_blink_rate': [20],
            'eye_closure_duration': [0.3],
            'fatigue_score': [0.5],
            'filename': ['default.jpg'],
            'category': ['default']
        })

    def integrate_datasets(self):
        """
        Integrate all datasets and create a combined dataset.

        Returns:
            DataFrame containing the integrated dataset
        """
        try:
            # Load features from each dataset
            keyboard_features = self.load_keyboard_data()
            mouse_features = self.load_mouse_data()
            facial_features = self.load_facial_data()

            # Create a new row with all features
            # Note: Voice features and time-based features are set to default values
            # as they're not available in the current datasets
            integrated_data = {
                # Keyboard features
                'typing_speed': keyboard_features['typing_speed'],
                'error_rate': keyboard_features['error_rate'],
                'pause_frequency': keyboard_features['pause_frequency'],
                'key_press_duration': keyboard_features['key_press_duration'],

                # Mouse features
                'movement_speed': mouse_features['movement_speed'],
                'click_frequency': mouse_features['click_frequency'],

                # Facial features
                'eye_blink_rate': facial_features['eye_blink_rate'],
                'eye_closure_duration': facial_features['eye_closure_duration'],

                # Voice features (default values)
                'speech_rate': 120,  # default value
                'pitch_variation': 0.8,  # default value
                'volume': 0.9,  # default value
                'clarity': 0.85,  # default value

                # Time-based features (default values)
                'hour_of_day': 12,  # default value
                'day_of_week': 1,  # default value

                # Target variable (to be determined)
                'fatigue_score': 0.5  # default value
            }

            # Create DataFrame
            df = pd.DataFrame([integrated_data])

            # Save integrated dataset
            output_path = os.path.join(self.base_dir, 'fatique', 'datasets', 'data', 'integrated_dataset.csv')
            df.to_csv(output_path, index=False)

            return df

        except Exception as e:
            print(f"Error integrating datasets: {str(e)}")
            return None

    def update_default_dataset(self):
        """
        Update the default dataset with the integrated data.
        """
        try:
            # Load the default dataset
            default_data_path = os.path.join(self.base_dir, 'fatique', 'datasets', 'data', 'default.csv')
            default_df = pd.read_csv(default_data_path)

            # Integrate new data
            integrated_df = self.integrate_datasets()

            if integrated_df is not None:
                # Append new data to default dataset
                updated_df = pd.concat([default_df, integrated_df], ignore_index=True)

                # Save updated dataset
                updated_df.to_csv(default_data_path, index=False)

                print("Default dataset updated successfully!")
                return True
            return False

        except Exception as e:
            print(f"Error updating default dataset: {str(e)}")
            return False