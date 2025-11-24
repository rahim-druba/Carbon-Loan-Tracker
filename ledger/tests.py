import pytest
from ledger.calculations import calculate_co2, calculate_required_trees
from ledger.models import CarbonLedger
from django.contrib.auth import get_user_model

User = get_user_model()

def test_calculate_co2():
    data = {
        'public_transport_km': 1000, # 0.2 tonnes
        'private_vehicle_km': 1000, # 0.4 tonnes
    }
    # Total 0.6
    assert calculate_co2(data) == pytest.approx(0.6)

def test_calculate_required_trees():
    # 0.6 tonnes / 0.5 = 1.2 -> ceil -> 2
    assert calculate_required_trees(0.6) == 2

@pytest.mark.django_db
def test_ledger_creation():
    user = User.objects.create_user('testuser', 'test@example.com', 'pass')
    ledger = CarbonLedger.objects.create(user=user, year=2023, total_co2_tonnes=1.0, required_trees=2)
    assert ledger.status == 'UNPAID'
    assert str(ledger) == 'testuser - 2023'
