"""
URL configuration for mental_fatique project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.shortcuts import redirect

# Redirect function to ensure data collection happens before dashboard access
def dashboard_redirect(request):
    # In a real app, you would check if the user has completed data collection
    # For now, always redirect to data collection
    return redirect('data_collection')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/fatigue/', include('fatigue_analysis.urls')),
    path('dashboard/', dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/view/', TemplateView.as_view(template_name='dashboard/index.html'), name='dashboard'),
    path('data_collection/', TemplateView.as_view(template_name='data_collection.html'), name='data_collection'),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]
