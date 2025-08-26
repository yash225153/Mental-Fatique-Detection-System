from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from utils.fatigue_detector import FatigueDetector
import numpy as np

# Global fatigue detector instance
fatigue_detector = FatigueDetector()

@login_required
def predict_fatigue(request):
    if request.method == 'POST':
        fatigue_score, confidence = fatigue_detector.predict_fatigue(request.user)
        
        if fatigue_score is not None:
            return JsonResponse({
                'fatigue_score': fatigue_score * 100,
                'confidence': confidence * 100
            })
        else:
            return JsonResponse({
                'error': 'Not enough data for prediction'
            }, status=400)
    
    return render(request, 'ml_models/prediction.html')

@login_required
def train_model(request):
    if request.method == 'POST':
        # TODO: Implement model training with real data
        # For now, using dummy data
        X_train = np.random.rand(100, 10, 2)
        y_train = np.random.randint(0, 2, size=(100, 1))
        
        fatigue_detector.train_model(X_train, y_train)
        
        return JsonResponse({
            'status': 'Model trained successfully'
        })
    
    return render(request, 'ml_models/training.html')

@login_required
def get_recommendations(request):
    if request.method == 'POST':
        # Get latest fatigue level
        latest_fatigue = fatigue_detector.predict_fatigue(request.user)
        
        if latest_fatigue[0] is not None:
            fatigue_score = latest_fatigue[0]
            
            # Generate recommendations based on fatigue level
            if fatigue_score > 0.8:
                recommendations = [
                    {
                        'type': 'break',
                        'text': 'Take a 15-minute break and go for a walk',
                        'priority': 1
                    },
                    {
                        'type': 'hydration',
                        'text': 'Drink some water to stay hydrated',
                        'priority': 2
                    }
                ]
            elif fatigue_score > 0.5:
                recommendations = [
                    {
                        'type': 'stretch',
                        'text': 'Take a 5-minute stretch break',
                        'priority': 1
                    },
                    {
                        'type': 'task',
                        'text': 'Switch to a different type of task',
                        'priority': 2
                    }
                ]
            else:
                recommendations = [
                    {
                        'type': 'maintain',
                        'text': 'Continue working at your current pace',
                        'priority': 1
                    }
                ]
            
            return JsonResponse({
                'recommendations': recommendations
            })
        else:
            return JsonResponse({
                'error': 'Not enough data for recommendations'
            }, status=400)
    
    return render(request, 'ml_models/recommendations.html') 