import os
import django
import random
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carbon_loan_tracker.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Vehicle, OnayCard, Property
from ledger.models import CarbonLedger, UsageLog, ConversionRate
from planting.models import TreeTransaction

User = get_user_model()

print('Seeding enhanced data...')

# 1. Create Conversion Rate
ConversionRate.objects.update_or_create(
    year=2025,
    defaults={'co2_per_tree': 0.02} # 20kg per tree
)

# 2. Create Special Users
# Analytics
if not User.objects.filter(username='analytics').exists():
    User.objects.create_user(
        username='analytics',
        email='analytics@example.com',
        password='password123',
        role=User.Role.ANALYTICS
    )
    print('Created analytics user')

# Admin
if not User.objects.filter(username='admin_user').exists():
    User.objects.create_user(
        username='admin_user',
        email='admin@example.com',
        password='password123',
        role=User.Role.ADMIN
    )
    print('Created admin user')

# Agent
if not User.objects.filter(username='agent_user').exists():
    User.objects.create_user(
        username='agent_user',
        email='agent@example.com',
        password='password123',
        role=User.Role.AGENT
    )
    print('Created agent user')

# 3. Create 50 Citizens
first_names = ['Ali', 'Aruzhan', 'Bakyt', 'Dana', 'Erzhan', 'Gulnaz', 'Kairat', 'Madina', 'Nursultan', 'Zarina']
last_names = ['Abayev', 'Bolat', 'Daulet', 'Ermek', 'Khasenov', 'Nurgaliyev', 'Ospanov', 'Serik', 'Tulegenov', 'Zhaksylyk']
cities = ['Almaty', 'Astana', 'Shymkent', 'Karaganda', 'Aktau']

for i in range(50):
    username = f'citizen_{i+1}'
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@example.com',
            'role': User.Role.CITIZEN,
            'city': random.choice(cities),
            'phone_number': f'+770{random.randint(10000000, 99999999)}',
            'date_of_birth': datetime.date(1980 + random.randint(0, 20), random.randint(1, 12), random.randint(1, 28))
        }
    )
    
    if created:
        user.set_password('password123')
        user.save()

    # Add Assets if none exist
    if not user.vehicles.exists() and random.choice([True, False]):
        Vehicle.objects.create(
            user=user,
            license_plate=f'{random.randint(100, 999)}ABC{random.randint(0, 99)}',
            make_model=random.choice(['Toyota Camry', 'Hyundai Accent', 'Kia Rio', 'Lada Granta', 'Tesla Model 3']),
            fuel_type=random.choice(['PETROL', 'DIESEL', 'ELECTRIC', 'HYBRID'])
        )
    
    if not user.onay_cards.exists() and random.choice([True, True, False]):
        OnayCard.objects.create(
            user=user,
            card_number=str(random.randint(1000000000, 9999999999))
        )
    
    if not user.properties.exists():
        Property.objects.create(
            user=user,
            address=f'{random.randint(1, 200)} Abay Ave, {user.city}',
            area_sqm=random.randint(30, 150),
            heating_type=random.choice(['GAS', 'ELECTRIC', 'CENTRAL'])
        )

    # Generate Usage Logs for 2025 if none exist
    if not user.usage_logs.filter(date__year=2025).exists():
        total_co2 = 0
        start_date = datetime.date(2025, 1, 1)
        end_date = datetime.date(2025, 12, 31)
        current_date = start_date
        
        while current_date <= end_date:
            # Randomly generate usage
            if random.random() < 0.3: # 30% chance of usage per day
                usage_type = random.choice(UsageLog.UsageType.choices)[0]
                amount = random.randint(5, 100)
                
                # Rough CO2 calc
                co2 = 0
                if usage_type == 'YANDEX':
                    co2 = amount * 0.0002 # 200g/km
                elif usage_type == 'ONAY':
                    co2 = amount * 0.00005 # 50g/km
                elif usage_type == 'PRIVATE_CAR':
                    co2 = amount * 0.00015 # 150g/km
                elif usage_type == 'BILLING':
                    co2 = amount * 0.0005 # 500g/kWh
                else:
                    co2 = amount * 0.0001

                UsageLog.objects.create(
                    user=user,
                    date=current_date,
                    usage_type=usage_type,
                    amount=amount,
                    co2_emitted=co2,
                    description=f"Usage on {current_date}"
                )
                total_co2 += co2
            
            current_date += datetime.timedelta(days=1)

        # Update Ledger
        ledger, _ = CarbonLedger.objects.get_or_create(user=user, year=2025)
        ledger.total_co2_tonnes = total_co2
        ledger.required_trees = int(total_co2 / 0.02) # Using 0.02 as rate
        ledger.save()

print('Successfully seeded 50 citizens with assets and 2025 data')
