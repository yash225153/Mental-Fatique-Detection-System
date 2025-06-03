from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    work_hours_per_day = models.FloatField(default=8.0)
    baseline_productivity = models.FloatField(default=0.0)  # Baseline productivity score
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class BehavioralData(models.Model):
    DATA_TYPE_CHOICES = [
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
        ('facial', 'Facial'),
        ('voice', 'Voice'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behavioral_data')
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES)
    raw_data = models.JSONField()  # Store raw data as JSON
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s {self.data_type} data at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

class KeyboardMetrics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='keyboard_metrics')
    typing_speed = models.FloatField()  # Words per minute
    error_rate = models.FloatField()  # Percentage of errors
    pause_frequency = models.FloatField()  # Number of pauses per minute
    key_press_duration = models.FloatField()  # Average duration of key presses in ms
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s keyboard metrics at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

class MouseMetrics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mouse_metrics')
    movement_speed = models.FloatField()  # Pixels per second
    click_frequency = models.FloatField()  # Clicks per minute
    movement_pattern = models.JSONField()  # Store movement patterns as JSON
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s mouse metrics at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

class FacialMetrics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='facial_metrics')
    eye_blink_rate = models.FloatField()  # Blinks per minute
    eye_closure_duration = models.FloatField()  # Average duration of eye closure in ms
    facial_expression = models.CharField(max_length=50)  # Dominant facial expression
    head_position = models.JSONField()  # Head position data as JSON
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s facial metrics at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

class VoiceMetrics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voice_metrics')
    speech_rate = models.FloatField()  # Words per minute
    pitch_variation = models.FloatField()  # Standard deviation of pitch
    volume = models.FloatField()  # Average volume level
    clarity = models.FloatField()  # Speech clarity score
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s voice metrics at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

class FatigueAnalysis(models.Model):
    FATIGUE_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('severe', 'Severe'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fatigue_analyses')
    fatigue_level = models.CharField(max_length=20, choices=FATIGUE_LEVEL_CHOICES)
    fatigue_score = models.FloatField()  # Numerical score from 0-100
    confidence = models.FloatField()  # ML model confidence (0-1)
    contributing_factors = models.JSONField()  # Factors contributing to fatigue as JSON
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s fatigue analysis at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Fatigue Analyses"

class ProductivityRecommendation(models.Model):
    RECOMMENDATION_TYPE_CHOICES = [
        ('break', 'Take a Break'),
        ('exercise', 'Physical Exercise'),
        ('meditation', 'Meditation'),
        ('task_switch', 'Switch Tasks'),
        ('environment', 'Change Environment'),
        ('nutrition', 'Nutrition Advice'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productivity_recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPE_CHOICES)
    description = models.TextField()
    expected_impact = models.FloatField()  # Expected productivity improvement (0-1)
    duration = models.IntegerField()  # Recommended duration in minutes
    timestamp = models.DateTimeField(default=timezone.now)
    implemented = models.BooleanField(default=False)  # Whether the user implemented the recommendation
    effectiveness = models.FloatField(null=True, blank=True)  # User-reported effectiveness (0-1)

    def __str__(self):
        return f"{self.user.username}'s {self.recommendation_type} recommendation at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

class ProductivitySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productivity_sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    productivity_score = models.FloatField(null=True, blank=True)  # Overall productivity score (0-100)
    fatigue_progression = models.JSONField(null=True, blank=True)  # Fatigue levels throughout session
    recommendations_followed = models.ManyToManyField(ProductivityRecommendation, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s session from {self.start_time} to {self.end_time or 'ongoing'}"

    def duration_minutes(self):
        if not self.end_time:
            return None
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 60

    class Meta:
        ordering = ['-start_time']

# New Model for Task Performance
class TaskPerformance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_performances')
    task_label = models.CharField(max_length=255) # Name or description of the task
    performance_score = models.FloatField() # A score representing performance (e.g., 0-100)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s performance on '{self.task_label}' at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Task Performances"

# New Model for Attention Data
class AttentionData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attention_data')
    attention_level = models.FloatField() # Attention level (e.g., 0-100)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s attention level at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Attention Data"
