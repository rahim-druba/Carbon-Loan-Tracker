@login_required
def trip_planner(request):
    """AI-powered CO2 trip prediction for citizens using pre-trained model"""
    if not request.user.is_citizen():
        messages.error(request, 'This feature is only available for citizens.')
        return redirect('dashboard')
    
    prediction = None
    
    if request.method == 'POST':
        import pickle
        import pandas as pd
        import os
        from django.conf import settings
        
        # Get form data
        car_model = request.POST.get('car_model')
        distance = float(request.POST.get('distance', 0))
        month = int(request.POST.get('month', 1))
        temperature = float(request.POST.get('temperature', 0))
        traffic_type = request.POST.get('traffic_type')
        
        try:
            # Load model and encoders
            model_dir = os.path.join(settings.BASE_DIR, 'predictor_models')
            
            with open(os.path.join(model_dir, 'car_model.pkl'), 'rb') as f:
                model = pickle.load(f)
            with open(os.path.join(model_dir, 'car_encoder.pkl'), 'rb') as f:
                car_encoder = pickle.load(f)
            with open(os.path.join(model_dir, 'traffic_encoder.pkl'), 'rb') as f:
                traffic_encoder = pickle.load(f)
            
            # Prepare input (Month, Temp, Dist, Car, Traffic)
            input_df = pd.DataFrame([[
                month,
                temperature,
                distance,
                car_encoder.transform([car_model])[0],
                traffic_encoder.transform([traffic_type])[0]
            ]], columns=['Month', 'Temp', 'Dist', 'Car', 'Traffic'])
            
            # Predict
            predicted_co2_kg = model.predict(input_df)[0]
            
            # Calculate offset (1 tree absorbs ~20kg CO2 per year)
            trees_needed = max(1, round(predicted_co2_kg / 20, 2))
            impact_level = "HIGH" if predicted_co2_kg > 10 else "MEDIUM" if predicted_co2_kg > 5 else "LOW"
            
            # Get comparison data (average for same distance)
            avg_co2 = distance * 0.15  # Average 150g/km
            savings = round(avg_co2 - predicted_co2_kg, 2)
            
            prediction = {
                'car_model': car_model,
                'distance': distance,
                'month': month,
                'temperature': temperature,
                'traffic_type': traffic_type,
                'co2_kg': round(predicted_co2_kg, 2),
                'trees_needed': trees_needed,
                'impact_level': impact_level,
                'savings': savings,
                'is_efficient': savings > 0
            }
            
        except Exception as e:
            messages.error(request, f'Prediction error: {str(e)}')
    
    # Load car list for dropdown
    import pickle
    import os
    from django.conf import settings
    model_dir = os.path.join(settings.BASE_DIR, 'predictor_models')
    
    with open(os.path.join(model_dir, 'car_list.pkl'), 'rb') as f:
        car_list = pickle.load(f)
    
    context = {
        'car_list': car_list,
        'prediction': prediction,
        'months': [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ],
        'traffic_types': [
            ('City_Jam', 'City (Heavy Traffic)'),
            ('City_Free', 'City (Free Flow)'),
            ('Highway', 'Highway')
        ]
    }
    
    return render(request, 'frontend/trip_planner.html', context)
