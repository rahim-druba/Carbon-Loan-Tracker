from django.core.management.base import BaseCommand
from accounts.models import User, District, Company, FriendRequest, MLPrediction
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Populates the database with demo data for Social and Analytics features'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating demo data...')

        # Districts
        districts_data = [
            ('Almaly', 'Almaty'), ('Medeu', 'Almaty'), ('Bostandyk', 'Almaty'),
            ('Esil', 'Astana'), ('Saryarka', 'Astana'), ('Almaty', 'Astana'),
            ('Kazybek Bi', 'Karaganda'), ('Oktyabr', 'Karaganda')
        ]
        districts = []
        for name, city in districts_data:
            d, created = District.objects.get_or_create(name=name, city=city)
            d.green_score = random.uniform(50, 95)
            d.save()
            districts.append(d)
        self.stdout.write(f'Created {len(districts)} districts.')

        # Companies
        companies_data = [
            ('Kaspi.kz', 'Fintech'), ('Air Astana', 'Aviation'), ('KazMunayGas', 'Energy'),
            ('Kazakhtelecom', 'Telecom'), ('Halyk Bank', 'Banking'), ('Chocofamily', 'Tech'),
            ('Technodom', 'Retail'), ('Magnum', 'Retail')
        ]
        companies = []
        for name, industry in companies_data:
            c, created = Company.objects.get_or_create(name=name, industry=industry)
            c.green_score = random.uniform(40, 90)
            c.save()
            companies.append(c)
        self.stdout.write(f'Created {len(companies)} companies.')

        # Users
        users = []
        for i in range(20):
            username = f'citizen_{i+1}'
            email = f'citizen_{i+1}@example.com'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=email, password='password123')
                user.role = User.Role.CITIZEN
                user.current_carbon_score = random.uniform(300, 800)
                user.district = random.choice(districts)
                user.company = random.choice(companies) if random.random() > 0.3 else None
                user.save()
                users.append(user)
        
        # Add a main demo user if not exists
        if not User.objects.filter(username='demo_citizen').exists():
            demo_user = User.objects.create_user('demo_citizen', 'demo@example.com', 'password123')
            demo_user.role = User.Role.CITIZEN
            demo_user.current_carbon_score = 650
            demo_user.district = districts[0]
            demo_user.company = companies[0]
            demo_user.save()
            users.append(demo_user)
        else:
            demo_user = User.objects.get(username='demo_citizen')

        self.stdout.write(f'Created/Ensured {len(users)} users.')

        # Friendships
        # Make demo_user friends with some random users
        potential_friends = [u for u in users if u != demo_user]
        random.shuffle(potential_friends)
        
        for friend in potential_friends[:5]:
            if not demo_user.friends.filter(pk=friend.pk).exists():
                demo_user.friends.add(friend)
                friend.friends.add(demo_user)
                # Create accepted request record
                FriendRequest.objects.get_or_create(
                    from_user=friend, to_user=demo_user, 
                    defaults={'status': 'ACCEPTED'}
                )

        # Create some pending requests
        for friend in potential_friends[5:8]:
             FriendRequest.objects.get_or_create(
                from_user=friend, to_user=demo_user,
                defaults={'status': 'PENDING'}
            )
        
        self.stdout.write('Created friendships and requests.')

        # ML Predictions
        actions = [
            "Switch to public transport for 3 days a week.",
            "Install smart thermostat to reduce heating costs.",
            "Plant 5 more trees to offset current usage.",
            "Reduce air travel by 20% this year."
        ]
        
        for user in users:
            if not MLPrediction.objects.filter(user=user).exists():
                MLPrediction.objects.create(
                    user=user,
                    predicted_year_end_debt=round(random.uniform(1000, 5000), 2),
                    recommended_action=random.choice(actions),
                    confidence_score=random.uniform(0.75, 0.95)
                )
        
        self.stdout.write('Created ML predictions.')
        self.stdout.write(self.style.SUCCESS('Successfully populated demo data'))
