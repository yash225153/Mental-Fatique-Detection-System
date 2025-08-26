"""
API views for the mental fatigue detection system.
"""

from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json

from ..models import (
    UserProfile,
    BehavioralData,
    KeyboardMetrics,
    MouseMetrics,
    FacialMetrics,
    VoiceMetrics,
    FatigueAnalysis,
    ProductivityRecommendation,
    ProductivitySession
)

from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    BehavioralDataSerializer,
    KeyboardMetricsSerializer,
    MouseMetricsSerializer,
    FacialMetricsSerializer,
    VoiceMetricsSerializer,
    FatigueAnalysisSerializer,
    ProductivityRecommendationSerializer,
    ProductivitySessionSerializer,
    UserRegistrationSerializer,
    RecommendationFeedbackSerializer,
    FatigueHistorySerializer
)

from ..ml_models.fatigue_detector import FatigueDetector
from ..ml_models.recommendation_engine import RecommendationEngine

class UserRegistrationView(generics.CreateAPIView):
    """API endpoint for user registration."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserProfileViewSet(viewsets.ModelViewSet):
    """API endpoint for user profiles."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset to only return the current user's profile."""
        return UserProfile.objects.filter(user=self.request.user)

class BehavioralDataViewSet(viewsets.ModelViewSet):
    """API endpoint for behavioral data."""
    queryset = BehavioralData.objects.all()
    serializer_class = BehavioralDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset to only return the current user's data."""
        return BehavioralData.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a new object."""
        serializer.save(user=self.request.user)

class KeyboardMetricsViewSet(viewsets.ModelViewSet):
    """API endpoint for keyboard metrics."""
    queryset = KeyboardMetrics.objects.all()
    serializer_class = KeyboardMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset to only return the current user's data."""
        return KeyboardMetrics.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a new object."""
        serializer.save(user=self.request.user)

class MouseMetricsViewSet(viewsets.ModelViewSet):
    """API endpoint for mouse metrics."""
    queryset = MouseMetrics.objects.all()
    serializer_class = MouseMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset to only return the current user's data."""
        return MouseMetrics.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a new object."""
        serializer.save(user=self.request.user)

class FacialMetricsViewSet(viewsets.ModelViewSet):
    """API endpoint for facial metrics."""
    queryset = FacialMetrics.objects.all()
    serializer_class = FacialMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset to only return the current user's data."""
        return FacialMetrics.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a new object."""
        serializer.save(user=self.request.user)

class VoiceMetricsViewSet(viewsets.ModelViewSet):
    """API endpoint for voice metrics."""
    queryset = VoiceMetrics.objects.all()
    serializer_class = VoiceMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset to only return the current user's data."""
        return VoiceMetrics.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a new object."""
        serializer.save(user=self.request.user)

class FatigueAnalysisViewSet(viewsets.ModelViewSet):
    """API endpoint for fatigue analysis."""
    queryset = FatigueAnalysis.objects.all()
    serializer_class = FatigueAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset to only return the current user's data."""
        return FatigueAnalysis.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current fatigue analysis."""
        # Get the latest fatigue analysis
        latest = FatigueAnalysis.objects.filter(user=request.user).order_by('-timestamp').first()
        
        if latest:
            # Check if it's recent (within the last hour)
            if latest.timestamp > timezone.now() - timedelta(hours=1):
                serializer = self.get_serializer(latest)
                return Response(serializer.data)
        
        # If no recent analysis, generate a new one
        detector = FatigueDetector()
        analysis = detector.predict(request.user)
        
        # Return the analysis
        return Response(analysis)
    
    @action(detail=False, methods=['post'])
    def history(self, request):
        """Get historical fatigue data."""
        serializer = FatigueHistorySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        interval = serializer.validated_data['interval']
        
        # Get fatigue analyses in the date range
        analyses = FatigueAnalysis.objects.filter(
            user=request.user,
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).order_by('timestamp')
        
        # Group by interval
        data = []
        
        if interval == 'hour':
            # Group by hour
            hour_data = {}
            
            for analysis in analyses:
                hour_key = analysis.timestamp.strftime('%Y-%m-%d %H:00')
                
                if hour_key not in hour_data:
                    hour_data[hour_key] = {
                        'timestamp': hour_key,
                        'fatigue_scores': [],
                        'count': 0
                    }
                
                hour_data[hour_key]['fatigue_scores'].append(analysis.fatigue_score)
                hour_data[hour_key]['count'] += 1
            
            # Calculate averages
            for hour_key, hour_info in hour_data.items():
                data.append({
                    'timestamp': hour_key,
                    'fatigue_score': sum(hour_info['fatigue_scores']) / hour_info['count'],
                    'count': hour_info['count']
                })
        
        elif interval == 'day':
            # Group by day
            day_data = {}
            
            for analysis in analyses:
                day_key = analysis.timestamp.strftime('%Y-%m-%d')
                
                if day_key not in day_data:
                    day_data[day_key] = {
                        'timestamp': day_key,
                        'fatigue_scores': [],
                        'count': 0
                    }
                
                day_data[day_key]['fatigue_scores'].append(analysis.fatigue_score)
                day_data[day_key]['count'] += 1
            
            # Calculate averages
            for day_key, day_info in day_data.items():
                data.append({
                    'timestamp': day_key,
                    'fatigue_score': sum(day_info['fatigue_scores']) / day_info['count'],
                    'count': day_info['count']
                })
        
        elif interval == 'week':
            # Group by week
            week_data = {}
            
            for analysis in analyses:
                week_key = analysis.timestamp.strftime('%Y-%U')
                
                if week_key not in week_data:
                    week_data[week_key] = {
                        'timestamp': week_key,
                        'fatigue_scores': [],
                        'count': 0
                    }
                
                week_data[week_key]['fatigue_scores'].append(analysis.fatigue_score)
                week_data[week_key]['count'] += 1
            
            # Calculate averages
            for week_key, week_info in week_data.items():
                data.append({
                    'timestamp': week_key,
                    'fatigue_score': sum(week_info['fatigue_scores']) / week_info['count'],
                    'count': week_info['count']
                })
        
        return Response(data)

class ProductivityRecommendationViewSet(viewsets.ModelViewSet):
    """API endpoint for productivity recommendations."""
    queryset = ProductivityRecommendation.objects.all()
    serializer_class = ProductivityRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset to only return the current user's data."""
        return ProductivityRecommendation.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get a current recommendation."""
        # Get the latest fatigue analysis
        latest_fatigue = FatigueAnalysis.objects.filter(user=request.user).order_by('-timestamp').first()
        
        # Generate a recommendation
        engine = RecommendationEngine()
        recommendation = engine.get_recommendation(request.user, latest_fatigue)
        
        return Response(recommendation)
    
    @action(detail=False, methods=['post'])
    def feedback(self, request):
        """Provide feedback on a recommendation."""
        serializer = RecommendationFeedbackSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        recommendation_id = serializer.validated_data['recommendation_id']
        implemented = serializer.validated_data['implemented']
        effectiveness = serializer.validated_data['effectiveness']
        
        try:
            # Get the recommendation
            recommendation = ProductivityRecommendation.objects.get(id=recommendation_id, user=request.user)
            
            # Update the recommendation
            recommendation.implemented = implemented
            recommendation.effectiveness = effectiveness
            recommendation.save()
            
            # Update the model if implemented
            if implemented:
                engine = RecommendationEngine()
                engine.update_model(request.user, recommendation_id, effectiveness)
            
            return Response({'status': 'success'})
        
        except ProductivityRecommendation.DoesNotExist:
            return Response(
                {'error': 'Recommendation not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class ProductivitySessionViewSet(viewsets.ModelViewSet):
    """API endpoint for productivity sessions."""
    queryset = ProductivitySession.objects.all()
    serializer_class = ProductivitySessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset to only return the current user's data."""
        return ProductivitySession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a new object."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current productivity session."""
        # Get the latest session that hasn't ended
        current_session = ProductivitySession.objects.filter(
            user=request.user,
            end_time__isnull=True
        ).order_by('-start_time').first()
        
        if current_session:
            serializer = self.get_serializer(current_session)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'No active session found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """Start a new productivity session."""
        # Check if there's already an active session
        active_session = ProductivitySession.objects.filter(
            user=request.user,
            end_time__isnull=True
        ).exists()
        
        if active_session:
            return Response(
                {'error': 'There is already an active session'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a new session
        session = ProductivitySession.objects.create(
            user=request.user,
            start_time=timezone.now()
        )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a productivity session."""
        try:
            session = ProductivitySession.objects.get(pk=pk, user=request.user)
            
            if session.end_time is not None:
                return Response(
                    {'error': 'Session has already ended'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # End the session
            session.end_time = timezone.now()
            
            # Calculate productivity score (simplified)
            # In a real application, you would use a more sophisticated approach
            fatigue_analyses = FatigueAnalysis.objects.filter(
                user=request.user,
                timestamp__gte=session.start_time,
                timestamp__lte=session.end_time
            ).order_by('timestamp')
            
            if fatigue_analyses:
                # Calculate average fatigue score
                avg_fatigue = sum(a.fatigue_score for a in fatigue_analyses) / len(fatigue_analyses)
                
                # Invert fatigue score to get productivity score (simplified)
                session.productivity_score = 100 - avg_fatigue
                
                # Store fatigue progression
                session.fatigue_progression = {
                    'timestamps': [a.timestamp.isoformat() for a in fatigue_analyses],
                    'scores': [a.fatigue_score for a in fatigue_analyses]
                }
            
            session.save()
            
            serializer = self.get_serializer(session)
            return Response(serializer.data)
        
        except ProductivitySession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """Get data for the dashboard."""
    try:
    # Get the latest fatigue analysis
    latest_fatigue = FatigueAnalysis.objects.filter(user=request.user).order_by('-timestamp').first()
    
        if not latest_fatigue:
            # If no fatigue analysis exists, create one
            detector = FatigueDetector()
            analysis = detector.predict(request.user)
            latest_fatigue = FatigueAnalysis.objects.filter(user=request.user).order_by('-timestamp').first()
    
    # Get recent fatigue history (last 24 hours)
    recent_fatigue = FatigueAnalysis.objects.filter(
        user=request.user,
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).order_by('timestamp')
    
    fatigue_history = []
    for analysis in recent_fatigue:
        fatigue_history.append({
            'timestamp': analysis.timestamp.isoformat(),
            'fatigue_score': analysis.fatigue_score,
            'fatigue_level': analysis.fatigue_level
        })
    
    # Get recent recommendations
        engine = RecommendationEngine()
        recommendations = engine.get_recommendation(request.user, latest_fatigue)
        
        # Calculate productivity score based on recent sessions
        recent_sessions = ProductivitySession.objects.filter(
            user=request.user,
            end_time__isnull=False,
            end_time__gte=timezone.now() - timedelta(hours=24)
        )
        
        productivity_score = 0
        if recent_sessions.exists():
            total_score = sum(session.productivity_score for session in recent_sessions)
            productivity_score = total_score / recent_sessions.count()
        
        # Calculate focus level based on keyboard and mouse metrics
        keyboard_metrics = KeyboardMetrics.objects.filter(
            user=request.user,
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).order_by('-timestamp').first()
        
        mouse_metrics = MouseMetrics.objects.filter(
            user=request.user,
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).order_by('-timestamp').first()
        
        focus_level = 0
        if keyboard_metrics and mouse_metrics:
            # Calculate focus based on typing speed and mouse movement
            typing_score = min(keyboard_metrics.typing_speed / 60, 1) * 50  # Max 50 points
            mouse_score = min(mouse_metrics.movement_speed / 100, 1) * 50  # Max 50 points
            focus_level = typing_score + mouse_score
        
        # Calculate stress level based on facial metrics
        facial_metrics = FacialMetrics.objects.filter(
        user=request.user,
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).order_by('-timestamp').first()
        
        stress_level = 0
        if facial_metrics:
            # Calculate stress based on eye blink rate and facial expressions
            blink_score = min(facial_metrics.eye_blink_rate / 20, 1) * 50  # Max 50 points
            expression_score = 50 if facial_metrics.facial_expression == 'stressed' else 0
            stress_level = blink_score + expression_score
    
    # Compile dashboard data
    dashboard = {
        'current_fatigue': {
                'score': latest_fatigue.fatigue_score,
                'level': latest_fatigue.fatigue_level,
                'timestamp': latest_fatigue.timestamp.isoformat(),
                'contributing_factors': latest_fatigue.contributing_factors
        },
            'recent_recommendations': [recommendations],
        'fatigue_history': fatigue_history,
            'productivity_score': round(productivity_score),
            'focus_level': round(focus_level),
            'stress_level': round(stress_level)
    }
    
    return Response(dashboard)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def data_collection(request):
    """Handle collected data from the data collection page."""
    try:
        data = request.data
        
        # Save keyboard metrics
        if data.get('typing'):
            typing_data = data['typing']
            KeyboardMetrics.objects.create(
                user=request.user,
                typing_speed=typing_data.get('typingSpeed', 0),
                error_rate=typing_data.get('errorRate', 0),
                pause_frequency=typing_data.get('pauseFrequency', 0),
                key_press_duration=typing_data.get('keyPressDuration', 0),
                timestamp=timezone.now()
            )
        
        # Save mouse metrics
        if data.get('mouse'):
            mouse_data = data['mouse']
            MouseMetrics.objects.create(
                user=request.user,
                movement_speed=mouse_data.get('movementSpeed', 0),
                click_frequency=mouse_data.get('clickFrequency', 0),
                movement_pattern=mouse_data.get('movementPattern', {}),
                timestamp=timezone.now()
            )
        
        # Save facial metrics
        if data.get('facial'):
            facial_data = data['facial']
            FacialMetrics.objects.create(
                user=request.user,
                eye_blink_rate=facial_data.get('blinkRate', 0),
                eye_closure_duration=facial_data.get('eyeClosure', 0),
                facial_expression=facial_data.get('expression', 'neutral'),
                timestamp=timezone.now()
            )
        
        # Generate fatigue analysis
        detector = FatigueDetector()
        analysis = detector.predict(request.user)
        
        return Response({'status': 'success'})
        
    except Exception as e:
        return Response(
            {'status': 'error', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
