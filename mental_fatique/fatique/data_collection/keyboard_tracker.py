"""
Keyboard tracking module for mental fatigue detection.
Captures typing patterns and calculates metrics.
"""

import time
from pynput import keyboard
from django.utils import timezone
from ..models import BehavioralData, KeyboardMetrics
import json
import threading
import numpy as np

class KeyboardTracker:
    def __init__(self, user):
        self.user = user
        self.key_presses = []
        self.key_releases = []
        self.key_press_times = {}  # Key: key, Value: press time
        self.errors = 0
        self.total_keys = 0
        self.is_tracking = False
        self.listener = None
        self.lock = threading.Lock()
        
    def on_press(self, key):
        """Callback function for key press events."""
        try:
            with self.lock:
                timestamp = time.time()
                key_char = key.char if hasattr(key, 'char') else str(key)
                self.key_press_times[key_char] = timestamp
                self.key_presses.append({
                    'key': key_char,
                    'timestamp': timestamp
                })
                self.total_keys += 1
        except Exception as e:
            print(f"Error in on_press: {e}")
    
    def on_release(self, key):
        """Callback function for key release events."""
        try:
            with self.lock:
                timestamp = time.time()
                key_char = key.char if hasattr(key, 'char') else str(key)
                
                # Calculate key press duration if we have the press time
                duration = None
                if key_char in self.key_press_times:
                    duration = timestamp - self.key_press_times[key_char]
                    del self.key_press_times[key_char]
                
                self.key_releases.append({
                    'key': key_char,
                    'timestamp': timestamp,
                    'duration': duration
                })
                
                # Check for backspace as a potential error correction
                if key == keyboard.Key.backspace:
                    self.errors += 1
        except Exception as e:
            print(f"Error in on_release: {e}")
    
    def start_tracking(self):
        """Start tracking keyboard activity."""
        if not self.is_tracking:
            self.is_tracking = True
            self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.listener.start()
            print("Keyboard tracking started")
    
    def stop_tracking(self):
        """Stop tracking keyboard activity."""
        if self.is_tracking and self.listener:
            self.listener.stop()
            self.is_tracking = False
            print("Keyboard tracking stopped")
    
    def calculate_metrics(self):
        """Calculate keyboard metrics from collected data."""
        with self.lock:
            # Calculate typing speed (keys per minute)
            if not self.key_presses:
                return None
            
            first_press = self.key_presses[0]['timestamp']
            last_press = self.key_presses[-1]['timestamp']
            
            # Avoid division by zero
            if last_press == first_press:
                typing_duration_minutes = 0.016  # Assume 1 second if same timestamp
            else:
                typing_duration_minutes = (last_press - first_press) / 60
            
            typing_speed = self.total_keys / max(typing_duration_minutes, 0.016)
            
            # Calculate error rate
            error_rate = (self.errors / max(self.total_keys, 1)) * 100
            
            # Calculate pause frequency (pauses per minute)
            pauses = 0
            for i in range(1, len(self.key_presses)):
                time_diff = self.key_presses[i]['timestamp'] - self.key_presses[i-1]['timestamp']
                if time_diff > 1.0:  # Pause defined as > 1 second between keypresses
                    pauses += 1
            
            pause_frequency = pauses / max(typing_duration_minutes, 0.016)
            
            # Calculate average key press duration
            durations = [release['duration'] for release in self.key_releases if release['duration'] is not None]
            key_press_duration = np.mean(durations) * 1000 if durations else 0  # Convert to milliseconds
            
            return {
                'typing_speed': typing_speed,
                'error_rate': error_rate,
                'pause_frequency': pause_frequency,
                'key_press_duration': key_press_duration
            }
    
    def save_data(self):
        """Save the collected data and metrics to the database."""
        with self.lock:
            # Save raw data
            raw_data = {
                'key_presses': self.key_presses,
                'key_releases': self.key_releases
            }
            
            BehavioralData.objects.create(
                user=self.user,
                data_type='keyboard',
                raw_data=raw_data,
                timestamp=timezone.now()
            )
            
            # Calculate and save metrics
            metrics = self.calculate_metrics()
            if metrics:
                KeyboardMetrics.objects.create(
                    user=self.user,
                    typing_speed=metrics['typing_speed'],
                    error_rate=metrics['error_rate'],
                    pause_frequency=metrics['pause_frequency'],
                    key_press_duration=metrics['key_press_duration'],
                    timestamp=timezone.now()
                )
            
            # Reset data
            self.key_presses = []
            self.key_releases = []
            self.key_press_times = {}
            self.errors = 0
            self.total_keys = 0
