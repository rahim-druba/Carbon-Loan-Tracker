
@login_required
def train_planner(request):
    """AI-powered CO2 prediction for train travel using pre-trained model"""
    if not request.user.is_citizen():
        messages.error(request, 'This feature is only available for citizens.')
        return redirect('dashboard')
    
    import joblib
    import pandas as pd
    import os
    from django.conf import settings
    
    # Model metadata
    model_info = {
        'name': 'Train Travel CO2 Predictor',
        'training_records': 5000,
        'accuracy': 99.85,  # R² score * 100
        'mae': 0.52,  # Mean Absolute Error in kg CO2
        'features': ['Month', 'Distance (km)', 'Train Type', 'Ticket Class']
    }
    
    prediction = None
    
    if request.method == 'POST':
        train_type = request.POST.get('train_type')
        ticket_class = request.POST.get('ticket_class')
        distance = int(request.POST.get('distance', 0))
        month = int(request.POST.get('month', 1))
        
        try:
            # Load model artifacts
            model_dir = os.path.join(settings.BASE_DIR, 'predictor_models')
            artifacts = joblib.load(os.path.join(model_dir, 'train_model_artifacts.joblib'))
            
            model = artifacts['model']
            le_train = artifacts['le_train']
            le_class = artifacts['le_class']
            
            # Prepare input
            t_code = le_train.transform([train_type])[0]
            c_code = le_class.transform([ticket_class])[0]
            
            input_df = pd.DataFrame([[month, distance, t_code, c_code]], 
                                   columns=['Month', 'Distance_KM', 'Train_Type', 'Class'])
            
            # Predict
            predicted_co2_kg = model.predict(input_df)[0]
            
            # Calculate trees needed (1 tree absorbs ~20kg CO2 per year)
            trees_needed = max(1, round(predicted_co2_kg / 20, 2))
            impact_level = "HIGH" if predicted_co2_kg > 100 else "MEDIUM" if predicted_co2_kg > 30 else "LOW"
            
            prediction = {
                'train_type': train_type,
                'ticket_class': ticket_class,
                'distance': distance,
                'month': month,
                'co2_kg': round(predicted_co2_kg, 2),
                'trees_needed': trees_needed,
                'impact_level': impact_level
            }
            
        except Exception as e:
            messages.error(request, f'Prediction error: {str(e)}')
    
    # Prepare context
    train_types = [
        'Talgo (High-Speed)',
        'Standard Electric',
        'Diesel Locomotive',
        'Commuter (Elektrichka)'
    ]
    
    ticket_classes = [
        'Seating (Common)',
        'Platskart (Dorm)',
        'Coupe (4-Berth)',
        'SV / Luxe (2-Berth)'
    ]
    
    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    context = {
        'train_types': train_types,
        'ticket_classes': ticket_classes,
        'months': months,
        'prediction': prediction,
        'model_info': model_info
    }
    
    return render(request, 'frontend/train_planner.html', context)
