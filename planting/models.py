from django.db import models
from django.conf import settings
from ledger.models import CarbonLedger

class TreeTransaction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    ledger = models.ForeignKey(CarbonLedger, on_delete=models.CASCADE, related_name='transactions')
    quantity = models.IntegerField()
    payment_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tx #{self.id} - {self.user.username} ({self.quantity} trees)"

class PlantingVerification(models.Model):
    transaction = models.OneToOneField(TreeTransaction, on_delete=models.CASCADE, related_name='verification')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='verifications')
    image_proof = models.ImageField(upload_to='planting_proofs/')
    location = models.CharField(max_length=255)
    planted_at = models.DateTimeField()
    
    # Admin approval
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_verifications')
    approved_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Verification for Tx #{self.transaction.id}"
