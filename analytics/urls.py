from django.urls import path
from . import views

urlpatterns = [
    path('reports/', views.generate_reports, name='generate_reports'),
    path('trends/', views.view_trends, name='view_trends'),
    path('export/', views.export_data, name='export_data'),
] 