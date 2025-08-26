"""
Facial analysis module for mental fatigue detection.
Captures facial expressions, eye movements, and calculates metrics.
"""

import cv2
import numpy as np
import time
import threading
import face_recognition
from django.utils import timezone
from ..models import BehavioralData, FacialMetrics
import json

class FacialAnalyzer:
    def __init__(self, user, camera_id=0):
        self.user = user
        self.camera_id = camera_id
        self.cap = None
        self.is_analyzing = False
        self.thread = None
        self.lock = threading.Lock()
        
        # Facial data storage
        self.blinks = []
        self.eye_aspects = []  # Eye aspect ratios over time
        self.facial_expressions = []
        self.head_positions = []
        
        # Blink detection parameters
        self.EYE_AR_THRESH = 0.2  # Eye aspect ratio threshold for blink detection
        self.EYE_AR_CONSEC_FRAMES = 3  # Number of consecutive frames for blink
        self.blink_counter = 0
        self.last_blink_time = None
        
    def eye_aspect_ratio(self, eye_landmarks):
        """Calculate the eye aspect ratio (EAR) for blink detection."""
        # Compute the euclidean distances between the vertical eye landmarks
        A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Compute the euclidean distance between the horizontal eye landmarks
        C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear
    
    def detect_blink(self, ear):
        """Detect blinks based on eye aspect ratio."""
        if ear < self.EYE_AR_THRESH:
            self.blink_counter += 1
        else:
            # If we had enough consecutive frames with low EAR, count as blink
            if self.blink_counter >= self.EYE_AR_CONSEC_FRAMES:
                current_time = time.time()
                
                # Record blink
                blink_data = {
                    'timestamp': current_time,
                    'duration': self.blink_counter / 30.0  # Assuming 30 fps
                }
                
                self.blinks.append(blink_data)
                
                # Update last blink time
                self.last_blink_time = current_time
                
            # Reset counter
            self.blink_counter = 0
    
    def analyze_frame(self, frame):
        """Analyze a single frame for facial features."""
        # Convert to RGB for face_recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find face locations and landmarks
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if face_locations:
            # Get the first face
            face_landmarks = face_recognition.face_landmarks(rgb_frame, face_locations)[0]
            
            # Get timestamp
            timestamp = time.time()
            
            # Extract eye landmarks
            left_eye = np.array([face_landmarks['left_eye']])
            right_eye = np.array([face_landmarks['right_eye']])
            
            # Calculate eye aspect ratios
            left_ear = self.eye_aspect_ratio(left_eye[0])
            right_ear = self.eye_aspect_ratio(right_eye[0])
            
            # Average the eye aspect ratio
            ear = (left_ear + right_ear) / 2.0
            
            # Detect blink
            self.detect_blink(ear)
            
            # Store eye aspect ratio
            self.eye_aspects.append({
                'timestamp': timestamp,
                'ear': ear
            })
            
            # Analyze facial expression (simplified)
            # In a real application, you would use a more sophisticated model
            mouth_width = np.linalg.norm(
                np.array(face_landmarks['top_lip'][0]) - 
                np.array(face_landmarks['top_lip'][6])
            )
            mouth_height = np.linalg.norm(
                np.array(face_landmarks['top_lip'][3]) - 
                np.array(face_landmarks['bottom_lip'][3])
            )
            
            # Simple expression detection based on mouth shape
            expression = 'neutral'
            if mouth_width > 60 and mouth_height < 20:
                expression = 'smiling'
            elif mouth_height > 30:
                expression = 'surprised'
            
            self.facial_expressions.append({
                'timestamp': timestamp,
                'expression': expression
            })
            
            # Extract head position (simplified)
            # In a real application, you would use a more sophisticated model
            nose_tip = np.array(face_landmarks['nose_tip'][0])
            chin = np.array(face_landmarks['chin'][0])
            
            head_position = {
                'timestamp': timestamp,
                'nose_tip_x': int(nose_tip[0]),
                'nose_tip_y': int(nose_tip[1]),
                'chin_x': int(chin[0]),
                'chin_y': int(chin[1])
            }
            
            self.head_positions.append(head_position)
            
            return True
        
        return False
    
    def analyze_video(self):
        """Continuously analyze video frames."""
        self.cap = cv2.VideoCapture(self.camera_id)
        
        while self.is_analyzing:
            ret, frame = self.cap.read()
            
            if not ret:
                print("Failed to grab frame")
                break
            
            with self.lock:
                self.analyze_frame(frame)
            
            # Add a small delay to reduce CPU usage
            time.sleep(0.03)  # ~30 fps
        
        # Release the camera
        if self.cap:
            self.cap.release()
    
    def start_analyzing(self):
        """Start analyzing facial features."""
        if not self.is_analyzing:
            self.is_analyzing = True
            self.thread = threading.Thread(target=self.analyze_video)
            self.thread.daemon = True
            self.thread.start()
            print("Facial analysis started")
    
    def stop_analyzing(self):
        """Stop analyzing facial features."""
        if self.is_analyzing:
            self.is_analyzing = False
            if self.thread:
                self.thread.join(timeout=1.0)
            print("Facial analysis stopped")
    
    def calculate_metrics(self):
        """Calculate facial metrics from collected data."""
        with self.lock:
            # Check if we have enough data
            if not self.eye_aspects or not self.facial_expressions:
                return None
            
            # Calculate blink rate (blinks per minute)
            if len(self.blinks) < 2:
                blink_rate = 0
            else:
                first_blink = self.blinks[0]['timestamp']
                last_blink = self.blinks[-1]['timestamp']
                duration_minutes = (last_blink - first_blink) / 60
                blink_rate = len(self.blinks) / max(duration_minutes, 0.016)
            
            # Calculate average eye closure duration
            if self.blinks:
                eye_closure_durations = [blink['duration'] * 1000 for blink in self.blinks]  # Convert to ms
                eye_closure_duration = np.mean(eye_closure_durations)
            else:
                eye_closure_duration = 0
            
            # Determine dominant facial expression
            if self.facial_expressions:
                expressions = [expr['expression'] for expr in self.facial_expressions]
                expression_counts = {}
                for expr in expressions:
                    expression_counts[expr] = expression_counts.get(expr, 0) + 1
                
                dominant_expression = max(expression_counts, key=expression_counts.get)
            else:
                dominant_expression = 'unknown'
            
            # Extract head position data
            if self.head_positions:
                head_position_data = {
                    'average_nose_tip_x': np.mean([pos['nose_tip_x'] for pos in self.head_positions]),
                    'average_nose_tip_y': np.mean([pos['nose_tip_y'] for pos in self.head_positions]),
                    'movement_variance_x': np.var([pos['nose_tip_x'] for pos in self.head_positions]),
                    'movement_variance_y': np.var([pos['nose_tip_y'] for pos in self.head_positions])
                }
            else:
                head_position_data = {
                    'average_nose_tip_x': 0,
                    'average_nose_tip_y': 0,
                    'movement_variance_x': 0,
                    'movement_variance_y': 0
                }
            
            return {
                'eye_blink_rate': blink_rate,
                'eye_closure_duration': eye_closure_duration,
                'facial_expression': dominant_expression,
                'head_position': head_position_data
            }
    
    def save_data(self):
        """Save the collected data and metrics to the database."""
        with self.lock:
            # Save raw data
            raw_data = {
                'blinks': self.blinks,
                'eye_aspects': self.eye_aspects,
                'facial_expressions': self.facial_expressions,
                'head_positions': self.head_positions
            }
            
            BehavioralData.objects.create(
                user=self.user,
                data_type='facial',
                raw_data=raw_data,
                timestamp=timezone.now()
            )
            
            # Calculate and save metrics
            metrics = self.calculate_metrics()
            if metrics:
                FacialMetrics.objects.create(
                    user=self.user,
                    eye_blink_rate=metrics['eye_blink_rate'],
                    eye_closure_duration=metrics['eye_closure_duration'],
                    facial_expression=metrics['facial_expression'],
                    head_position=metrics['head_position'],
                    timestamp=timezone.now()
                )
            
            # Reset data
            self.blinks = []
            self.eye_aspects = []
            self.facial_expressions = []
            self.head_positions = []
            self.blink_counter = 0
            self.last_blink_time = None
