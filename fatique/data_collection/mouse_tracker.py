"""
Mouse tracking module for mental fatigue detection.
Captures mouse movements, clicks, and calculates metrics.
"""

import time
from pynput import mouse
from django.utils import timezone
from ..models import BehavioralData, MouseMetrics
import json
import threading
import numpy as np
import math

class MouseTracker:
    def __init__(self, user):
        self.user = user
        self.movements = []
        self.clicks = []
        self.is_tracking = False
        self.listener = None
        self.lock = threading.Lock()
        self.last_position = None
        self.last_timestamp = None
    
    def on_move(self, x, y):
        """Callback function for mouse movement events."""
        try:
            with self.lock:
                timestamp = time.time()
                
                # Calculate speed if we have a previous position
                speed = None
                if self.last_position and self.last_timestamp:
                    dx = x - self.last_position[0]
                    dy = y - self.last_position[1]
                    distance = math.sqrt(dx**2 + dy**2)
                    time_diff = timestamp - self.last_timestamp
                    if time_diff > 0:
                        speed = distance / time_diff
                
                self.movements.append({
                    'x': x,
                    'y': y,
                    'timestamp': timestamp,
                    'speed': speed
                })
                
                self.last_position = (x, y)
                self.last_timestamp = timestamp
        except Exception as e:
            print(f"Error in on_move: {e}")
    
    def on_click(self, x, y, button, pressed):
        """Callback function for mouse click events."""
        try:
            with self.lock:
                timestamp = time.time()
                self.clicks.append({
                    'x': x,
                    'y': y,
                    'button': str(button),
                    'pressed': pressed,
                    'timestamp': timestamp
                })
        except Exception as e:
            print(f"Error in on_click: {e}")
    
    def on_scroll(self, x, y, dx, dy):
        """Callback function for mouse scroll events."""
        try:
            with self.lock:
                timestamp = time.time()
                self.movements.append({
                    'x': x,
                    'y': y,
                    'scroll_dx': dx,
                    'scroll_dy': dy,
                    'timestamp': timestamp,
                    'type': 'scroll'
                })
        except Exception as e:
            print(f"Error in on_scroll: {e}")
    
    def start_tracking(self):
        """Start tracking mouse activity."""
        if not self.is_tracking:
            self.is_tracking = True
            self.listener = mouse.Listener(
                on_move=self.on_move,
                on_click=self.on_click,
                on_scroll=self.on_scroll
            )
            self.listener.start()
            print("Mouse tracking started")
    
    def stop_tracking(self):
        """Stop tracking mouse activity."""
        if self.is_tracking and self.listener:
            self.listener.stop()
            self.is_tracking = False
            print("Mouse tracking stopped")
    
    def calculate_metrics(self):
        """Calculate mouse metrics from collected data."""
        with self.lock:
            # Check if we have enough data
            if not self.movements or not self.clicks:
                return None
            
            # Calculate average movement speed (pixels per second)
            speeds = [m['speed'] for m in self.movements if m.get('speed') is not None]
            movement_speed = np.mean(speeds) if speeds else 0
            
            # Calculate click frequency (clicks per minute)
            first_timestamp = min(
                self.movements[0]['timestamp'] if self.movements else float('inf'),
                self.clicks[0]['timestamp'] if self.clicks else float('inf')
            )
            
            last_timestamp = max(
                self.movements[-1]['timestamp'] if self.movements else float('-inf'),
                self.clicks[-1]['timestamp'] if self.clicks else float('-inf')
            )
            
            # Avoid division by zero
            if last_timestamp == first_timestamp:
                duration_minutes = 0.016  # Assume 1 second if same timestamp
            else:
                duration_minutes = (last_timestamp - first_timestamp) / 60
            
            click_frequency = len(self.clicks) / max(duration_minutes, 0.016)
            
            # Extract movement patterns (simplified)
            # For a real application, you might want to use more sophisticated pattern recognition
            movement_pattern = {
                'total_distance': sum(
                    math.sqrt((m['x'] - self.movements[i-1]['x'])**2 + 
                             (m['y'] - self.movements[i-1]['y'])**2)
                    for i, m in enumerate(self.movements) if i > 0
                ),
                'direction_changes': sum(
                    1 for i in range(2, len(self.movements)) if
                    (self.movements[i]['x'] - self.movements[i-1]['x']) * 
                    (self.movements[i-1]['x'] - self.movements[i-2]['x']) < 0 or
                    (self.movements[i]['y'] - self.movements[i-1]['y']) * 
                    (self.movements[i-1]['y'] - self.movements[i-2]['y']) < 0
                ),
                'click_positions': [(c['x'], c['y']) for c in self.clicks if c['pressed']]
            }
            
            return {
                'movement_speed': movement_speed,
                'click_frequency': click_frequency,
                'movement_pattern': movement_pattern
            }
    
    def save_data(self):
        """Save the collected data and metrics to the database."""
        with self.lock:
            # Save raw data
            raw_data = {
                'movements': self.movements,
                'clicks': self.clicks
            }
            
            BehavioralData.objects.create(
                user=self.user,
                data_type='mouse',
                raw_data=raw_data,
                timestamp=timezone.now()
            )
            
            # Calculate and save metrics
            metrics = self.calculate_metrics()
            if metrics:
                MouseMetrics.objects.create(
                    user=self.user,
                    movement_speed=metrics['movement_speed'],
                    click_frequency=metrics['click_frequency'],
                    movement_pattern=metrics['movement_pattern'],
                    timestamp=timezone.now()
                )
            
            # Reset data
            self.movements = []
            self.clicks = []
            self.last_position = None
            self.last_timestamp = None
