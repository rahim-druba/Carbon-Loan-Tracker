import math

# Conversion factors (tonnes per unit)
FACTORS = {
    'public_transport_km': 0.0002,
    'ride_hailing_km': 0.00025,
    'private_vehicle_km': 0.0004,
    'electricity_kwh': 0.0000004,
    'heating_kwh': 0.0000009,
}

TREE_OFFSET_TONNES = 0.5

def calculate_co2(data):
    """
    Calculate total CO2 tonnes based on input data dictionary.
    data keys should match FACTORS keys.
    """
    total_tonnes = 0
    for key, factor in FACTORS.items():
        value = data.get(key, 0)
        total_tonnes += value * factor
    return total_tonnes

def calculate_required_trees(total_tonnes):
    """
    Calculate required trees to offset CO2.
    Formula: ceil(total_co2_tonnes / 0.5)
    """
    return math.ceil(total_tonnes / TREE_OFFSET_TONNES)
