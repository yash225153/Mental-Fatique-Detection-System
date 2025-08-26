import pyaudio
import numpy as np
import librosa
import json
from datetime import datetime
from data_collection.models import UserBehavior

class VoiceAnalyzer:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        
    def analyze_audio(self, audio_data):
        # Convert to numpy array
        audio_np = np.frombuffer(audio_data, dtype=np.float32)
        
        # Extract features
        mfcc = librosa.feature.mfcc(y=audio_np, sr=self.RATE, n_mfcc=13)
        pitch = librosa.yin(audio_np, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        energy = librosa.feature.rms(y=audio_np)
        
        # Calculate statistics
        mfcc_mean = np.mean(mfcc, axis=1)
        mfcc_std = np.std(mfcc, axis=1)
        pitch_mean = np.mean(pitch[~np.isnan(pitch)])
        energy_mean = np.mean(energy)
        
        return {
            'mfcc_mean': mfcc_mean.tolist(),
            'mfcc_std': mfcc_std.tolist(),
            'pitch_mean': float(pitch_mean),
            'energy_mean': float(energy_mean)
        }
    
    def start_recording(self, user, duration=5):
        stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        print(f"Recording for {duration} seconds...")
        frames = []
        
        for i in range(0, int(self.RATE / self.CHUNK * duration)):
            data = stream.read(self.CHUNK)
            frames.append(data)
        
        print("Finished recording")
        stream.stop_stream()
        stream.close()
        
        # Analyze the recording
        audio_data = b''.join(frames)
        features = self.analyze_audio(audio_data)
        
        # Save to database
        UserBehavior.objects.create(
            user=user,
            voice_analysis_data=json.dumps(features)
        )
        
        return features
    
    def __del__(self):
        self.p.terminate() 