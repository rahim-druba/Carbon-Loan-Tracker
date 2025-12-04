import pickle
from sklearn.preprocessing import LabelEncoder

# Car models from the training data
car_list = [
    'Toyota Camry',
    'Chevrolet Cobalt', 
    'Toyota Land Cruiser Prado',
    'Hyundai Accent',
    'Lexus LX',
    'Daewoo Nexia'
]

# Traffic types from the training data
traffic_list = ['City_Jam', 'City_Free', 'Highway']

# Create and fit encoders
le_car = LabelEncoder()
le_car.fit(car_list)

le_traffic = LabelEncoder()
le_traffic.fit(traffic_list)

# Save encoders
with open('predictor_models/car_encoder.pkl', 'wb') as f:
    pickle.dump(le_car, f)

with open('predictor_models/traffic_encoder.pkl', 'wb') as f:
    pickle.dump(le_traffic, f)

with open('predictor_models/car_list.pkl', 'wb') as f:
    pickle.dump(car_list, f)

print("✅ Encoders created successfully!")
print("   - car_encoder.pkl")
print("   - traffic_encoder.pkl") 
print("   - car_list.pkl")
