
@login_required
def predictors_hub(request):
    """Central hub for all CO2 emission predictors"""
    if not request.user.is_citizen():
        messages.error(request, 'This feature is only available for citizens.')
        return redirect('dashboard')
    
    return render(request, 'frontend/predictors_hub.html')
