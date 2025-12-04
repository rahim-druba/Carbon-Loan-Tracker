from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ledger.models import CarbonLedger
from planting.models import TreeTransaction, PlantingVerification
from ledger.calculations import calculate_required_trees
import random
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Loads sample data for Carbon Loan Tracker'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading sample data...')

        # Create Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Created superuser: admin/admin123')

        # Create Agents
        agents = []
        for i in range(1, 3):
            username = f'agent{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username, f'agent{i}@example.com', 'password123', role=User.Role.AGENT)
                agents.append(user)
                self.stdout.write(f'Created agent: {username}/password123')
            else:
                agents.append(User.objects.get(username=username))

        # Create Citizens
        citizens = []
        for i in range(1, 11):
            username = f'citizen{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username, f'citizen{i}@example.com', 'password123', role=User.Role.CITIZEN)
                citizens.append(user)
                self.stdout.write(f'Created citizen: {username}/password123')
            else:
                citizens.append(User.objects.get(username=username))

        # Create Ledgers
        for citizen in citizens:
            for year in [2023, 2024]:
                if not CarbonLedger.objects.filter(user=citizen, year=year).exists():
                    co2 = random.uniform(5.0, 20.0)
                    trees = calculate_required_trees(co2)
                    CarbonLedger.objects.create(
                        user=citizen,
                        year=year,
                        total_co2_tonnes=co2,
                        required_trees=trees,
                        status=CarbonLedger.Status.UNPAID
                    )

        # Create Transactions
        for citizen in citizens:
            # Randomly create a transaction
            if random.choice([True, False]):
                ledger = CarbonLedger.objects.filter(user=citizen).first()
                qty = random.randint(1, ledger.required_trees)
                tx = TreeTransaction.objects.create(
                    user=citizen,
                    ledger=ledger,
                    quantity=qty,
                    payment_reference=f'PAY-{random.randint(1000,9999)}',
                    status=TreeTransaction.Status.PENDING
                )
                
                # Randomly verify
                if random.choice([True, False]):
                    tx.status = TreeTransaction.Status.APPROVED
                    tx.save()
                    
                    PlantingVerification.objects.create(
                        transaction=tx,
                        agent=random.choice(agents),
                        location=f'Forest Zone {random.randint(1, 5)}',
                        planted_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                        is_verified=True,
                        image_proof='planting_proofs/sample.jpg' # Assuming this exists or will be handled gracefully
                    )

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data'))
