import pytest
from planting.models import TreeTransaction
from ledger.models import CarbonLedger
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_transaction_flow():
    user = User.objects.create_user('citizen', 'c@e.com', 'pass')
    ledger = CarbonLedger.objects.create(user=user, year=2023, total_co2_tonnes=1, required_trees=2)
    
    tx = TreeTransaction.objects.create(
        user=user,
        ledger=ledger,
        quantity=2,
        payment_reference='REF123'
    )
    
    assert tx.status == 'PENDING'
    assert tx.user == user
