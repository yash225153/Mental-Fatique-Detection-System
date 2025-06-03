"""
URL configuration for the API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'behavioral-data', views.BehavioralDataViewSet)
router.register(r'keyboard-metrics', views.KeyboardMetricsViewSet)
router.register(r'mouse-metrics', views.MouseMetricsViewSet)
router.register(r'facial-metrics', views.FacialMetricsViewSet)
router.register(r'voice-metrics', views.VoiceMetricsViewSet)
router.register(r'fatigue-analysis', views.FatigueAnalysisViewSet)
router.register(r'recommendations', views.ProductivityRecommendationViewSet)
router.register(r'sessions', views.ProductivitySessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('dashboard/', views.dashboard_data, name='dashboard'),
    path('keyboard/', views.keyboard_metrics, name='keyboard_metrics'),
    path('mouse/', views.mouse_metrics, name='mouse_metrics'),
    path('facial/', views.facial_metrics, name='facial_metrics'),
]
