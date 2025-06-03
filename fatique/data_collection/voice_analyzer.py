"""
Voice analysis module for mental fatigue detection.
Captures voice patterns and calculates metrics.
"""

import numpy as np
import librosa
import sounddevice as sd
import threading
import time
import queue
from django.utils import timezone
from ..models import BehavioralData, VoiceMetrics

class VoiceAnalyzer:
    def __init__(self, user, sample_rate=16000, duration=5):
        self.user = user
        self.sample_rate = sample_rate
        self.duration = duration  # Recording duration in seconds
        self.is_analyzing = False
        self.thread = None
        self.lock = threading.Lock()
        self.audio_queue = queue.Queue()
        
        # Voice data storage
        self.recordings = []
        self.speech_features = []
    
    def record_audio(self):
        """Record audio from the microphone."""
        try:
            print(f"Recording for {self.duration} seconds...")
            audio_data = sd.rec(
                int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                blocking=True
            )
            print("Recording complete")
            
            # Flatten and normalize
            audio_data = audio_data.flatten()
            audio_data = audio_data / np.max(np.abs(audio_data))
            
            return audio_data
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None
    
    def extract_features(self, audio_data):
        """Extract features from audio data."""
        try:
            # Extract various audio features
            
            # Mel-frequency cepstral coefficients
            mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
            mfccs_mean = np.mean(mfccs, axis=1)
            
            # Root Mean Square Energy
            rms = librosa.feature.rms(y=audio_data)[0]
            rms_mean = np.mean(rms)
            
            # Zero Crossing Rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            zcr_mean = np.mean(zcr)
            
            # Spectral Centroid
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)[0]
            spectral_centroid_mean = np.mean(spectral_centroid)
            
            # Spectral Bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=self.sample_rate)[0]
            spectral_bandwidth_mean = np.mean(spectral_bandwidth)
            
            # Pitch (fundamental frequency)
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=self.sample_rate)
            pitch_mean = 0
            pitch_std = 0
            
            if np.any(magnitudes > 0):
                pitch_indices = np.argmax(magnitudes, axis=0)
                pitches_valid = np.take_along_axis(pitches, pitch_indices.reshape(1, -1), axis=0).flatten()
                pitches_valid = pitches_valid[pitches_valid > 0]
                
                if len(pitches_valid) > 0:
                    pitch_mean = np.mean(pitches_valid)
                    pitch_std = np.std(pitches_valid)
            
            # Estimate speech rate (simplified)
            # In a real application, you would use a more sophisticated model
            onsets = librosa.onset.onset_detect(y=audio_data, sr=self.sample_rate)
            speech_rate = len(onsets) / self.duration * 60  # Onsets per minute as proxy for words
            
            features = {
                'timestamp': time.time(),
                'mfccs': mfccs_mean.tolist(),
                'rms': float(rms_mean),
                'zcr': float(zcr_mean),
                'spectral_centroid': float(spectral_centroid_mean),
                'spectral_bandwidth': float(spectral_bandwidth_mean),
                'pitch_mean': float(pitch_mean),
                'pitch_std': float(pitch_std),
                'speech_rate': float(speech_rate)
            }
            
            return features
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def analyze_voice(self):
        """Continuously analyze voice."""
        while self.is_analyzing:
            # Record audio
            audio_data = self.record_audio()
            
            if audio_data is not None:
                with self.lock:
                    # Store recording
                    self.recordings.append({
                        'timestamp': time.time(),
                        'duration': self.duration,
                        'sample_rate': self.sample_rate
                    })
                    
                    # Extract and store features
                    features = self.extract_features(audio_data)
                    if features:
                        self.speech_features.append(features)
                        
                        # Add to queue for real-time processing
                        self.audio_queue.put(features)
            
            # Add a small delay between recordings
            time.sleep(1.0)
    
    def start_analyzing(self):
        """Start analyzing voice."""
        if not self.is_analyzing:
            self.is_analyzing = True
            self.thread = threading.Thread(target=self.analyze_voice)
            self.thread.daemon = True
            self.thread.start()
            print("Voice analysis started")
    
    def stop_analyzing(self):
        """Stop analyzing voice."""
        if self.is_analyzing:
            self.is_analyzing = False
            if self.thread:
                self.thread.join(timeout=1.0)
            print("Voice analysis stopped")
    
    def calculate_metrics(self):
        """Calculate voice metrics from collected data."""
        with self.lock:
            # Check if we have enough data
            if not self.speech_features:
                return None
            
            # Calculate speech rate (words per minute)
            speech_rates = [feature['speech_rate'] for feature in self.speech_features]
            speech_rate = np.mean(speech_rates)
            
            # Calculate pitch variation
            pitch_stds = [feature['pitch_std'] for feature in self.speech_features]
            pitch_variation = np.mean(pitch_stds)
            
            # Calculate volume (using RMS as proxy)
            volumes = [feature['rms'] for feature in self.speech_features]
            volume = np.mean(volumes)
            
            # Calculate clarity (using spectral centroid and bandwidth as proxy)
            # In a real application, you would use a more sophisticated model
            centroids = [feature['spectral_centroid'] for feature in self.speech_features]
            bandwidths = [feature['spectral_bandwidth'] for feature in self.speech_features]
            
            # Normalize and combine for a clarity score (0-1)
            norm_centroids = np.array(centroids) / max(max(centroids), 1)
            norm_bandwidths = 1 - (np.array(bandwidths) / max(max(bandwidths), 1))
            clarity = np.mean(0.7 * norm_centroids + 0.3 * norm_bandwidths)
            
            return {
                'speech_rate': speech_rate,
                'pitch_variation': pitch_variation,
                'volume': volume,
                'clarity': clarity
            }
    
    def save_data(self):
        """Save the collected data and metrics to the database."""
        with self.lock:
            # Save raw data
            raw_data = {
                'recordings': self.recordings,
                'speech_features': self.speech_features
            }
            
            BehavioralData.objects.create(
                user=self.user,
                data_type='voice',
                raw_data=raw_data,
                timestamp=timezone.now()
            )
            
            # Calculate and save metrics
            metrics = self.calculate_metrics()
            if metrics:
                VoiceMetrics.objects.create(
                    user=self.user,
                    speech_rate=metrics['speech_rate'],
                    pitch_variation=metrics['pitch_variation'],
                    volume=metrics['volume'],
                    clarity=metrics['clarity'],
                    timestamp=timezone.now()
                )
            
            # Reset data
            self.recordings = []
            self.speech_features = []
