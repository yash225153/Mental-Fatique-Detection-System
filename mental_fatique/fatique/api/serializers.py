"""
Serializers for the API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'age', 'occupation', 'work_hours_per_day', 'baseline_productivity', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class BehavioralDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehavioralData
        fields = ['id', 'user', 'data_type', 'raw_data', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class KeyboardMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyboardMetrics
        fields = ['id', 'user', 'typing_speed', 'error_rate', 'pause_frequency', 'key_press_duration', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class MouseMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MouseMetrics
        fields = ['id', 'user', 'movement_speed', 'click_frequency', 'movement_pattern', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class FacialMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacialMetrics
        fields = ['id', 'user', 'eye_blink_rate', 'eye_closure_duration', 'facial_expression', 'head_position', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class VoiceMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceMetrics
        fields = ['id', 'user', 'speech_rate', 'pitch_variation', 'volume', 'clarity', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class FatigueAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = FatigueAnalysis
        fields = ['id', 'user', 'fatigue_level', 'fatigue_score', 'confidence', 'contributing_factors', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class ProductivityRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductivityRecommendation
        fields = ['id', 'user', 'recommendation_type', 'description', 'expected_impact', 'duration', 'timestamp', 'implemented', 'effectiveness']
        read_only_fields = ['id', 'timestamp']

class ProductivitySessionSerializer(serializers.ModelSerializer):
    recommendations_followed = ProductivityRecommendationSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductivitySession
        fields = ['id', 'user', 'start_time', 'end_time', 'productivity_score', 'fatigue_progression', 'recommendations_followed', 'notes']
        read_only_fields = ['id']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    age = serializers.IntegerField(required=False)
    occupation = serializers.CharField(required=False, allow_blank=True)
    work_hours_per_day = serializers.FloatField(required=False, default=8.0)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'age', 'occupation', 'work_hours_per_day']
    
    def create(self, validated_data):
        age = validated_data.pop('age', None)
        occupation = validated_data.pop('occupation', '')
        work_hours_per_day = validated_data.pop('work_hours_per_day', 8.0)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        UserProfile.objects.create(
            user=user,
            age=age,
            occupation=occupation,
            work_hours_per_day=work_hours_per_day
        )
        
        return user

class RecommendationFeedbackSerializer(serializers.Serializer):
    recommendation_id = serializers.IntegerField()
    implemented = serializers.BooleanField()
    effectiveness = serializers.FloatField(min_value=0.0, max_value=1.0)

class FatigueHistorySerializer(serializers.Serializer):
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    interval = serializers.ChoiceField(choices=['hour', 'day', 'week'], default='day')
