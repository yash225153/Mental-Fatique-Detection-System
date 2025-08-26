from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import threading
import cv2
import base64
import numpy as np
from utils.behavior_tracker import BehaviorTracker
from utils.face_detector import FaceDetector
from utils.voice_analyzer import VoiceAnalyzer

# Store active trackers for each user
active_trackers = {}
face_detectors = {}
voice_analyzers = {}

@login_required
def collect_behavior_data(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'start':
            if request.user.id not in active_trackers:
                tracker = BehaviorTracker(request.user)
                thread = threading.Thread(target=tracker.start_tracking)
                thread.daemon = True
                thread.start()
                active_trackers[request.user.id] = tracker
                return JsonResponse({'status': 'started'})
            else:
                return JsonResponse({'status': 'already_running'})
        
        elif action == 'stop':
            if request.user.id in active_trackers:
                del active_trackers[request.user.id]
                return JsonResponse({'status': 'stopped'})
            else:
                return JsonResponse({'status': 'not_running'})
    
    return render(request, 'data_collection/behavior_tracking.html')

@csrf_exempt
@login_required
def collect_face_data(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'start':
            if request.user.id not in face_detectors:
                detector = FaceDetector()
                face_detectors[request.user.id] = detector
                return JsonResponse({'status': 'started'})
            else:
                return JsonResponse({'status': 'already_running'})
        
        elif action == 'stop':
            if request.user.id in face_detectors:
                del face_detectors[request.user.id]
                return JsonResponse({'status': 'stopped'})
            else:
                return JsonResponse({'status': 'not_running'})
        
        elif action == 'frame':
            if request.user.id in face_detectors:
                detector = face_detectors[request.user.id]
                frame_data = request.POST.get('frame')
                frame_bytes = base64.b64decode(frame_data)
                frame = cv2.imdecode(np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR)
                signals = detector.process_frame(frame, request.user)
                return JsonResponse({'signals': signals})
    
    return render(request, 'data_collection/face_tracking.html')

@csrf_exempt
@login_required
def collect_voice_data(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'start':
            if request.user.id not in voice_analyzers:
                analyzer = VoiceAnalyzer()
                thread = threading.Thread(target=analyzer.start_recording, args=(request.user,))
                thread.daemon = True
                thread.start()
                voice_analyzers[request.user.id] = analyzer
                return JsonResponse({'status': 'started'})
            else:
                return JsonResponse({'status': 'already_running'})
        
        elif action == 'stop':
            if request.user.id in voice_analyzers:
                del voice_analyzers[request.user.id]
                return JsonResponse({'status': 'stopped'})
            else:
                return JsonResponse({'status': 'not_running'})
    
    return render(request, 'data_collection/voice_tracking.html') 