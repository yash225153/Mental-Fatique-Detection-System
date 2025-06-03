"""
URL configuration for the frontend views.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tracking/start/', views.start_tracking, name='start_tracking'),
    path('tracking/stop/', views.stop_tracking, name='stop_tracking'),
    path('fatigue/analysis/', views.get_fatigue_analysis, name='get_fatigue_analysis'),
    path('recommendation/', views.get_recommendation, name='get_recommendation'),
    path('recommendation/feedback/', views.recommendation_feedback, name='recommendation_feedback'),
    path('session/start/', views.start_session, name='start_session'),
    path('session/<int:session_id>/end/', views.end_session, name='end_session'),
    path('api/dashboard/', views.dashboard_api, name='dashboard_api'),
]
