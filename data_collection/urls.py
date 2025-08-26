from django.urls import path
from . import views

urlpatterns = [
    path('behavior/', views.collect_behavior_data, name='collect_behavior'),
    path('face/', views.collect_face_data, name='collect_face'),
    path('voice/', views.collect_voice_data, name='collect_voice'),
] 