"""
URL configuration for fatigue analysis endpoints.
"""

from django.urls import path
from . import views

app_name = 'fatigue_analysis'

urlpatterns = [
    path('analyze/', views.analyze_fatigue, name='analyze_fatigue'),
    path('insights/', views.get_fatigue_insights, name='get_insights'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
