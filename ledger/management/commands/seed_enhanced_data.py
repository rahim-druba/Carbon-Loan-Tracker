import random
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds the database with enhanced sample data for 2025'

    def handle(self, *args, **kwargs):
        from django.contrib.auth import get_user_model
        from accounts.models import Vehicle, OnayCard, Property
        from ledger.models import CarbonLedger, UsageLog, ConversionRate
        from planting.models import TreeTransaction
        
        User = get_user_model()
        
        self.stdout.write('Seeding enhanced data...')

        # 1. Create Conversion Rate
        ConversionRate.objects.update_or_create(
            year=2025,
            defaults={'co2_per_tree': 0.02} # 20kg per tree
        )

        # 2. Create Analytics User
        if not User.objects.filter(username='analytics').exists():
            User.objects.create_user(
                username='analytics',
                email='analytics@example.com',
                password='password123',
                role=User.Role.ANALYTICS
            )
            self.stdout.write(self.style.SUCCESS('Created analytics user'))

        # 3. Create 50 Citizens
        first_names = ['Ali', 'Aruzhan', 'Bakyt', 'Dana', 'Erzhan', 'Gulnaz', 'Kairat', 'Madina', 'Nursultan', 'Zarina']
        last_names = ['Abayev', 'Bolat', 'Daulet', 'Ermek', 'Khasenov', 'Nurgaliyev', 'Ospanov', 'Serik', 'Tulegenov', 'Zhaksylyk']
        cities = ['Almaty', 'Astana', 'Shymkent', 'Karaganda', 'Aktau']

        for i in range(50):
            username = f'citizen_{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='password123',
                    role=User.Role.CITIZEN,
                    city=random.choice(cities),
                    phone_number=f'+770{random.randint(10000000, 99999999)}',
                    date_of_birth=datetime.date(1980 + random.randint(0, 20), random.randint(1, 12), random.randint(1, 28))
                )
                
                # Add Assets
                # Vehicle
                if random.choice([True, False]):
                    Vehicle.objects.create(
                        user=user,
                        license_plate=f'{random.randint(100, 999)}ABC{random.randint(0, 99)}',
                        make_model=random.choice(['Toyota Camry', 'Hyundai Accent', 'Kia Rio', 'Lada Granta', 'Tesla Model 3']),
                        fuel_type=random.choice(['PETROL', 'DIESEL', 'ELECTRIC', 'HYBRID'])
                    )
                
                # Onay Card
                if random.choice([True, True, False]): # More likely to have Onay
                    OnayCard.objects.create(
                        user=user,
                        card_number=str(random.randint(1000000000, 9999999999))
                    )
                
                # Property
                Property.objects.create(
                    user=user,
                    address=f'{random.randint(1, 200)} Abay Ave, {user.city}',
                    area_sqm=random.randint(30, 150),
                    heating_type=random.choice(['GAS', 'ELECTRIC', 'CENTRAL'])
                )

                # Generate Usage Logs for 2025
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

        self.stdout.write(self.style.SUCCESS('Successfully seeded 50 citizens with assets and 2025 data'))
