from django.db import models
from django.contrib.auth.models import User

class UserBehavior(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    typing_speed = models.FloatField(null=True, blank=True)
    mouse_movement_count = models.IntegerField(null=True, blank=True)
    face_detection_data = models.JSONField(null=True, blank=True)
    voice_analysis_data = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']

class FatigueLevel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    fatigue_score = models.FloatField()
    confidence = models.FloatField()
    data_source = models.CharField(max_length=50)  # typing, mouse, face, voice, combined
    
    class Meta:
        ordering = ['-timestamp']

class ProductivityRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    recommendation_type = models.CharField(max_length=50)
    recommendation_text = models.TextField()
    priority = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp'] 