
@login_required
def flight_planner(request):
    """AI-powered CO2 prediction for flight travel using pre-trained aviation model"""
    if not request.user.is_citizen():
        messages.error(request, 'This feature is only available for citizens.')
        return redirect('dashboard')
    
    import joblib
    import pandas as pd
    import os
    import math
    from django.conf import settings
    
    # Airport coordinates for distance calculation
    AIRPORT_COORDS = {
        'ALA': (43.35, 77.04, 'Almaty'),
        'NQZ': (51.02, 71.46, 'Astana'),
        'DXB': (25.25, 55.36, 'Dubai'),
        'IST': (41.27, 28.75, 'Istanbul'),
        'LHR': (51.47, -0.45, 'London'),
        'FRA': (50.03, 8.57, 'Frankfurt'),
        'ICN': (37.46, 126.44, 'Seoul'),
        'JFK': (40.64, -73.77, 'New York'),
        'BKK': (13.69, 100.75, 'Bangkok'),
        'CDG': (49.00, 2.55, 'Paris'),
    }
    
    def calculate_distance(code1, code2):
        if code1 not in AIRPORT_COORDS or code2 not in AIRPORT_COORDS:
            return 1000
        lat1, lon1 = AIRPORT_COORDS[code1][:2]
        lat2, lon2 = AIRPORT_COORDS[code2][:2]
        R = 6371
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2) * math.sin(dlambda/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    prediction = None
    
    if request.method == 'POST':
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        aircraft = request.POST.get('aircraft')
        cabin_class = request.POST.get('cabin_class')
        luggage = int(request.POST.get('luggage', 0))
        
        try:
            # Load model artifacts
            model_dir = os.path.join(settings.BASE_DIR, 'predictor_models')
            artifacts = joblib.load(os.path.join(model_dir, 'aviation_model_artifacts.joblib'))
            
            model = artifacts['model']
            le_aircraft = artifacts['le_aircraft']
            le_class = artifacts['le_class']
            
            # Calculate distance
            distance = calculate_distance(origin, destination)
            
            # Prepare input
            ac_code = le_aircraft.transform([aircraft])[0]
            cl_code = le_class.transform([cabin_class])[0]
            
            input_df = pd.DataFrame([[distance, ac_code, cl_code, luggage]], 
                                   columns=['Distance', 'Aircraft', 'Class', 'Luggage'])
            
            # Predict
            predicted_co2_kg = model.predict(input_df)[0]
            
            # Calculate trees needed (1 tree absorbs ~20kg CO2 per year)
            trees_needed = max(1, round(predicted_co2_kg / 20, 2))
            impact_level = "HIGH" if predicted_co2_kg > 500 else "MEDIUM" if predicted_co2_kg > 200 else "LOW"
            
            # Get airport names
            origin_name = AIRPORT_COORDS[origin][2]
            dest_name = AIRPORT_COORDS[destination][2]
            
            prediction = {
                'origin': origin,
                'origin_name': origin_name,
                'destination': destination,
                'dest_name': dest_name,
                'aircraft': aircraft,
                'cabin_class': cabin_class,
                'luggage': luggage,
                'distance': round(distance, 0),
                'co2_kg': round(predicted_co2_kg, 2),
                'trees_needed': trees_needed,
                'impact_level': impact_level
            }
            
        except Exception as e:
            messages.error(request, f'Prediction error: {str(e)}')
    
    # Prepare context
    aircraft_list = [
        'Airbus A320',
        'Boeing 737-800',
        'Boeing 777-300ER',
        'Airbus A350-900',
        'Embraer E190'
    ]
    
    airports = [
        ('ALA', 'Almaty (ALA)'),
        ('NQZ', 'Astana (NQZ)'),
        ('DXB', 'Dubai (DXB)'),
        ('IST', 'Istanbul (IST)'),
        ('LHR', 'London (LHR)'),
        ('FRA', 'Frankfurt (FRA)'),
        ('ICN', 'Seoul (ICN)'),
        ('JFK', 'New York (JFK)'),
        ('BKK', 'Bangkok (BKK)'),
        ('CDG', 'Paris (CDG)')
    ]
    
    cabin_classes = [
        ('Economy', 'Economy'),
        ('Business', 'Business'),
        ('First', 'First Class')
    ]
    
    context = {
        'aircraft_list': aircraft_list,
        'airports': airports,
        'cabin_classes': cabin_classes,
        'prediction': prediction
    }
    
    return render(request, 'frontend/flight_planner.html', context)
