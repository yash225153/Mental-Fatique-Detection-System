import cv2
import numpy as np
from datetime import datetime
import json
from data_collection.models import UserBehavior

class FaceDetector:
    def __init__(self):
        # Load face detection model
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # Load facial landmark detector
        self.face_mesh = cv2.FaceDetectorYN.create(
            "face_detection_yunet_2023mar.onnx",
            "",
            (320, 320),
            0.9,
            0.3,
            5000
        )
        
    def detect_fatigue_signals(self, frame):
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return None
        
        # Get the largest face
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face_roi = gray[y:y+h, x:x+w]
        
        # Calculate eye aspect ratio (EAR)
        # This is a simplified version - in practice, you'd use facial landmarks
        eye_region = face_roi[int(h*0.25):int(h*0.5), int(w*0.2):int(w*0.8)]
        _, eye_thresh = cv2.threshold(eye_region, 30, 255, cv2.THRESH_BINARY_INV)
        eye_contours, _ = cv2.findContours(eye_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Calculate mouth aspect ratio (MAR)
        mouth_region = face_roi[int(h*0.6):int(h*0.8), int(w*0.3):int(w*0.7)]
        _, mouth_thresh = cv2.threshold(mouth_region, 30, 255, cv2.THRESH_BINARY_INV)
        mouth_contours, _ = cv2.findContours(mouth_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Calculate fatigue indicators
        eye_area = sum(cv2.contourArea(c) for c in eye_contours)
        mouth_area = sum(cv2.contourArea(c) for c in mouth_contours)
        
        # Normalize by face area
        face_area = w * h
        normalized_eye_area = eye_area / face_area
        normalized_mouth_area = mouth_area / face_area
        
        return {
            'eye_aspect_ratio': normalized_eye_area,
            'mouth_aspect_ratio': normalized_mouth_area,
            'face_detected': True
        }
    
    def process_frame(self, frame, user):
        # Detect fatigue signals
        signals = self.detect_fatigue_signals(frame)
        
        if signals:
            # Save to database
            UserBehavior.objects.create(
                user=user,
                face_detection_data=json.dumps(signals)
            )
        
        return signals 