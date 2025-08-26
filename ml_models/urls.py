from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_fatigue, name='predict_fatigue'),
    path('train/', views.train_model, name='train_model'),
    path('recommend/', views.get_recommendations, name='get_recommendations'),
] 