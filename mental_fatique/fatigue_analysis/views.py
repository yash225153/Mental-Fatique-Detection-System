"""
Views for fatigue analysis and ML model integration.
"""

import json
import sys
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

# Add the ml_models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_models'))

try:
    from fatigue_predictor import predict_fatigue, get_recommendations
except ImportError:
    # Fallback if ML model is not available
    def predict_fatigue(typing_data=None, mouse_data=None, facial_data=None):
        return {
            'combined_fatigue_score': 45,
            'individual_scores': {'typing': 45, 'mouse': 45, 'facial': 45},
            'confidence': 0.5,
            'data_quality': {'typing_available': False, 'mouse_available': False, 'facial_available': False}
        }
    
    def get_recommendations(fatigue_score, individual_scores=None):
        return {
            'recommendations': [{'type': 'Break', 'action': 'Take a break', 'description': 'Rest for a while', 'duration': '10 minutes', 'priority': 'medium'}],
            'insights': ['No ML model available'],
            'fatigue_level': 'Moderate',
            'timestamp': '2024-01-01T00:00:00'
        }

@csrf_exempt
@require_http_methods(["POST"])
def analyze_fatigue(request):
    """
    Analyze fatigue based on collected data using ML models.
    
    Expected POST data:
    {
        "typing_data": {...},
        "mouse_data": {...},
        "facial_data": {...}
    }
    """
    try:
        # Parse the request data
        data = json.loads(request.body)
        
        typing_data = data.get('typing_data')
        mouse_data = data.get('mouse_data')
        facial_data = data.get('facial_data')
        
        # Use ML model to predict fatigue
        prediction_result = predict_fatigue(typing_data, mouse_data, facial_data)
        
        # Get personalized recommendations
        recommendations = get_recommendations(
            prediction_result['combined_fatigue_score'],
            prediction_result['individual_scores']
        )
        
        # Combine results
        response_data = {
            'status': 'success',
            'fatigue_analysis': prediction_result,
            'recommendations': recommendations,
            'message': 'Fatigue analysis completed successfully'
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Analysis failed: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_fatigue_insights(request):
    """
    Get insights and recommendations based on current fatigue level.
    """
    try:
        # Get fatigue score from query parameters
        fatigue_score = float(request.GET.get('fatigue_score', 45))
        
        # Get individual scores if provided
        typing_score = request.GET.get('typing_score')
        mouse_score = request.GET.get('mouse_score')
        facial_score = request.GET.get('facial_score')
        
        individual_scores = {}
        if typing_score:
            individual_scores['typing'] = float(typing_score)
        if mouse_score:
            individual_scores['mouse'] = float(mouse_score)
        if facial_score:
            individual_scores['facial'] = float(facial_score)
        
        # Get recommendations
        recommendations = get_recommendations(fatigue_score, individual_scores if individual_scores else None)
        
        return JsonResponse({
            'status': 'success',
            'recommendations': recommendations
        })
        
    except ValueError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid fatigue score format'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to get insights: {str(e)}'
        }, status=500)

def dashboard_view(request):
    """
    Render the dashboard with ML-enhanced insights.
    """
    # This view can be extended to pre-load ML insights
    context = {
        'ml_enabled': True,
        'default_fatigue_score': 45
    }
    return render(request, 'dashboard/index.html', context)
