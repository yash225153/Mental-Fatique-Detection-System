"""
Main data collection module that coordinates all trackers and analyzers.
"""

from .keyboard_tracker import KeyboardTracker
from .mouse_tracker import MouseTracker
from .facial_analyzer import FacialAnalyzer
from .voice_analyzer import VoiceAnalyzer
import threading
import time

class DataCollector:
    def __init__(self, user, collection_interval=60, save_interval=300):
        """
        Initialize the data collector.
        
        Args:
            user: The user to collect data for
            collection_interval: How often to collect data (in seconds)
            save_interval: How often to save data to the database (in seconds)
        """
        self.user = user
        self.collection_interval = collection_interval
        self.save_interval = save_interval
        
        # Initialize trackers and analyzers
        self.keyboard_tracker = KeyboardTracker(user)
        self.mouse_tracker = MouseTracker(user)
        self.facial_analyzer = FacialAnalyzer(user)
        self.voice_analyzer = VoiceAnalyzer(user)
        
        # Threading
        self.is_collecting = False
        self.collection_thread = None
        self.save_thread = None
    
    def start_collection(self):
        """Start collecting data from all sources."""
        if not self.is_collecting:
            self.is_collecting = True
            
            # Start individual trackers
            self.keyboard_tracker.start_tracking()
            self.mouse_tracker.start_tracking()
            self.facial_analyzer.start_analyzing()
            self.voice_analyzer.start_analyzing()
            
            # Start save thread
            self.save_thread = threading.Thread(target=self._save_loop)
            self.save_thread.daemon = True
            self.save_thread.start()
            
            print("Data collection started")
    
    def stop_collection(self):
        """Stop collecting data from all sources."""
        if self.is_collecting:
            self.is_collecting = False
            
            # Stop individual trackers
            self.keyboard_tracker.stop_tracking()
            self.mouse_tracker.stop_tracking()
            self.facial_analyzer.stop_analyzing()
            self.voice_analyzer.stop_analyzing()
            
            # Save final data
            self._save_data()
            
            # Wait for save thread to finish
            if self.save_thread:
                self.save_thread.join(timeout=1.0)
            
            print("Data collection stopped")
    
    def _save_data(self):
        """Save data from all trackers to the database."""
        self.keyboard_tracker.save_data()
        self.mouse_tracker.save_data()
        self.facial_analyzer.save_data()
        self.voice_analyzer.save_data()
        print("Data saved to database")
    
    def _save_loop(self):
        """Periodically save data to the database."""
        while self.is_collecting:
            # Sleep for the save interval
            time.sleep(self.save_interval)
            
            # Save data if still collecting
            if self.is_collecting:
                self._save_data()
    
    def get_current_metrics(self):
        """Get the current metrics from all trackers."""
        keyboard_metrics = self.keyboard_tracker.calculate_metrics()
        mouse_metrics = self.mouse_tracker.calculate_metrics()
        facial_metrics = self.facial_analyzer.calculate_metrics()
        voice_metrics = self.voice_analyzer.calculate_metrics()
        
        return {
            'keyboard': keyboard_metrics,
            'mouse': mouse_metrics,
            'facial': facial_metrics,
            'voice': voice_metrics
        }
