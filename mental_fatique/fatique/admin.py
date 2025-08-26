from django.contrib import admin
from .models import (
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

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'occupation', 'work_hours_per_day', 'baseline_productivity')
    search_fields = ('user__username', 'occupation')

@admin.register(BehavioralData)
class BehavioralDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'data_type', 'timestamp')
    list_filter = ('data_type', 'timestamp')
    search_fields = ('user__username',)

@admin.register(KeyboardMetrics)
class KeyboardMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'typing_speed', 'error_rate', 'pause_frequency', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username',)

@admin.register(MouseMetrics)
class MouseMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'movement_speed', 'click_frequency', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username',)

@admin.register(FacialMetrics)
class FacialMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'eye_blink_rate', 'facial_expression', 'timestamp')
    list_filter = ('facial_expression', 'timestamp')
    search_fields = ('user__username',)

@admin.register(VoiceMetrics)
class VoiceMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'speech_rate', 'volume', 'clarity', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username',)

@admin.register(FatigueAnalysis)
class FatigueAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'fatigue_level', 'fatigue_score', 'confidence', 'timestamp')
    list_filter = ('fatigue_level', 'timestamp')
    search_fields = ('user__username',)

@admin.register(ProductivityRecommendation)
class ProductivityRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'recommendation_type', 'expected_impact', 'implemented', 'timestamp')
    list_filter = ('recommendation_type', 'implemented', 'timestamp')
    search_fields = ('user__username', 'description')

@admin.register(ProductivitySession)
class ProductivitySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'productivity_score', 'duration_minutes')
    list_filter = ('start_time',)
    search_fields = ('user__username', 'notes')
