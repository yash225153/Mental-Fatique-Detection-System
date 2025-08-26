import time
from datetime import datetime
import json
from pynput import mouse, keyboard
from django.conf import settings
from data_collection.models import UserBehavior

class BehaviorTracker:
    def __init__(self, user):
        self.user = user
        self.typing_start_time = None
        self.typing_count = 0
        self.mouse_movement_count = 0
        self.last_save_time = time.time()
        self.save_interval = 60  # Save data every 60 seconds

    def on_press(self, key):
        if self.typing_start_time is None:
            self.typing_start_time = time.time()
        self.typing_count += 1

    def on_move(self, x, y):
        self.mouse_movement_count += 1

    def save_data(self):
        if self.typing_count > 0 and self.typing_start_time is not None:
            typing_duration = time.time() - self.typing_start_time
            typing_speed = (self.typing_count / 5) / (typing_duration / 60)  # WPM calculation
            
            UserBehavior.objects.create(
                user=self.user,
                typing_speed=typing_speed,
                mouse_movement_count=self.mouse_movement_count
            )
            
            # Reset counters
            self.typing_count = 0
            self.mouse_movement_count = 0
            self.typing_start_time = None
            self.last_save_time = time.time()

    def start_tracking(self):
        # Start keyboard listener
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        keyboard_listener.start()
        
        # Start mouse listener
        mouse_listener = mouse.Listener(on_move=self.on_move)
        mouse_listener.start()
        
        try:
            while True:
                if time.time() - self.last_save_time >= self.save_interval:
                    self.save_data()
                time.sleep(1)
        except KeyboardInterrupt:
            keyboard_listener.stop()
            mouse_listener.stop() 