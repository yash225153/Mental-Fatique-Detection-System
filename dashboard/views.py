from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from data_collection.models import UserBehavior, FatigueLevel, ProductivityRecommendation

@login_required
def dashboard(request):
    # Get latest user behavior data
    latest_behavior = UserBehavior.objects.filter(user=request.user).first()
    
    # Get latest fatigue level
    latest_fatigue = FatigueLevel.objects.filter(user=request.user).first()
    
    # Get active recommendations
    active_recommendations = ProductivityRecommendation.objects.filter(
        user=request.user,
        is_completed=False
    ).order_by('-priority')
    
    context = {
        'latest_behavior': latest_behavior,
        'latest_fatigue': latest_fatigue,
        'active_recommendations': active_recommendations,
    }
    
    return render(request, 'dashboard/index.html', context) 