from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
import json

from .models import (
    UserProfile,
    ProductivitySession,
    BehavioralData,
    FatigueAnalysis
)

from .ml_models.fatigue_detector import FatigueDetector
from .ml_models.recommendation_engine import RecommendationEngine
from .data_collection.data_collector import DataCollector

def index(request):
    """Render the home page."""
    return render(request, 'index.html')

@login_required
def dashboard(request):
    """Render the dashboard page."""
    return render(request, 'dashboard/index.html')

@login_required
def start_tracking(request):
    """Start tracking user behavior."""
    user = request.user

    # Check if a collector already exists for this user
    if not hasattr(request, 'data_collector'):
        # Create a new collector
        collector = DataCollector(user)
        request.data_collector = collector

    # Start collection
    request.data_collector.start_collection()

    return JsonResponse({'status': 'success', 'message': 'Tracking started'})

@login_required
def stop_tracking(request):
    """Stop tracking user behavior."""
    # Check if a collector exists
    if hasattr(request, 'data_collector'):
        # Stop collection
        request.data_collector.stop_collection()
        del request.data_collector

    return JsonResponse({'status': 'success', 'message': 'Tracking stopped'})

@login_required
def get_fatigue_analysis(request):
    """Get the current fatigue analysis."""
    user = request.user

    # Create a fatigue detector
    detector = FatigueDetector()

    # Get the analysis
    analysis = detector.predict(user)

    return JsonResponse(analysis)

@login_required
def get_recommendation(request):
    """Get a productivity recommendation."""
    user = request.user

    # Create a recommendation engine
    engine = RecommendationEngine()

    # Get a recommendation
    recommendation = engine.get_recommendation(user)

    return JsonResponse(recommendation)

@csrf_exempt
@login_required
def recommendation_feedback(request):
    """Process feedback on a recommendation."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        recommendation_id = data.get('recommendation_id')
        implemented = data.get('implemented', False)
        effectiveness = data.get('effectiveness', 0.0)

        # Create a recommendation engine
        engine = RecommendationEngine()

        # Update the model
        if implemented:
            engine.update_model(request.user, recommendation_id, effectiveness)

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def start_session(request):
    """Start a new productivity session."""
    user = request.user

    # Check if there's already an active session
    active_session = ProductivitySession.objects.filter(
        user=user,
        end_time__isnull=True
    ).exists()

    if active_session:
        return JsonResponse(
            {'status': 'error', 'message': 'There is already an active session'},
            status=400
        )

    # Create a new session
    session = ProductivitySession.objects.create(
        user=user,
        start_time=timezone.now()
    )

    # Start tracking
    start_tracking(request)

    return JsonResponse({
        'status': 'success',
        'session_id': session.id,
        'start_time': session.start_time.isoformat()
    })

@login_required
def end_session(request, session_id):
    """End a productivity session."""
    user = request.user

    try:
        session = ProductivitySession.objects.get(id=session_id, user=user)

        if session.end_time is not None:
            return JsonResponse(
                {'status': 'error', 'message': 'Session has already ended'},
                status=400
            )

        # End the session
        session.end_time = timezone.now()
        session.save()

        # Stop tracking
        stop_tracking(request)

        return JsonResponse({
            'status': 'success',
            'session_id': session.id,
            'end_time': session.end_time.isoformat(),
            'duration_minutes': session.duration_minutes()
        })

    except ProductivitySession.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Session not found'},
            status=404
        )

@login_required
def dashboard_api(request):
    """API endpoint to provide data for the dashboard."""
    user = request.user

    # 1. Get Current Fatigue Level and Score
    # Assuming FatigueDetector can provide the latest analysis for a user
    detector = FatigueDetector()
    current_fatigue_analysis = detector.predict(user)

    # Default structure if analysis fails or is incomplete
    current_fatigue_data = {
        "score": current_fatigue_analysis.get('score', 0) if current_fatigue_analysis else 0,
        "level": current_fatigue_analysis.get('level', 'Unknown') if current_fatigue_analysis else 'Unknown'
    }

    # 2. Get Fatigue History
    fatigue_history_data = []
    try:
        # Fetch recent fatigue analyses, ordered by timestamp
        # Use FatigueAnalysis model which has the fatigue_score field
        recent_analyses = FatigueAnalysis.objects.filter(user=user).order_by('-timestamp')[:50]
        fatigue_history_data = [{'timestamp': analysis.timestamp.isoformat(), 'score': analysis.fatigue_score} for analysis in recent_analyses]
    except Exception as e:
        print(f"Error fetching fatigue history: {e}")
        # Optionally, return an error in the JSON response or log it differently

    # 3. Get Task Performance Data
    # This requires a model or logic to track task performance.
    # Replace with actual data fetching from your models/logic when available.
    task_performance_data = [
        {"label": "Task 1", "performance": 85},
        {"label": "Task 2", "performance": 70},
        {"label": "Task 3", "performance": 90},
        {"label": "Task 4", "performance": 75},
        {"label": "Task 5", "performance": 80},
    ] # Placeholder data

    # 4. Get Recent Recommendations
    # Assuming RecommendationEngine can provide recent recommendations for a user.
    engine = RecommendationEngine()
    # You might need to add a method like get_recent_recommendations to your RecommendationEngine class
    # This method should return a list of strings.
    try:
        # Call the existing get_recommendation method
        recommendation_data = engine.get_recommendation(user)
        # Extract the description and put it in a list
        if recommendation_data and recommendation_data.get('description'):
            recent_recommendations_list = [recommendation_data.get('description')]
        else:
            recent_recommendations_list = [] # Empty list if no recommendation description
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        recent_recommendations_list = [] # Default to empty list on error

    # Default if no recommendations are found or an error occurred
    if not recent_recommendations_list:
         recent_recommendations_list = ["Take a short break", "Try mindfulness exercise", "Stay hydrated"]


    # 5. Get Attention Level
    # This requires a model or logic to track attention.
    # Replace with actual data fetching from your models/logic when available.
    attention_level_data = {"level": 60} # Placeholder data

    dashboard_data = {
        "current_fatigue": current_fatigue_data,
        "fatigue_history": fatigue_history_data,
        "task_performance_data": task_performance_data,
        "recent_recommendations": recent_recommendations_list,
        "attention_level": attention_level_data.get('level', 0) # Ensure only the level is passed
    }

    return JsonResponse(dashboard_data)
