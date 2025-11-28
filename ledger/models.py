from django.db import models
from django.conf import settings

class CarbonLedger(models.Model):
    class Status(models.TextChoices):
        UNPAID = 'UNPAID', 'Unpaid'
        PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially Paid'
        CLEARED = 'CLEARED', 'Cleared'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ledgers')
    year = models.IntegerField()
    total_co2_tonnes = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    required_trees = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNPAID)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'year')

    def __str__(self):
        return f"{self.user.username} - {self.year}"

class UsageLog(models.Model):
    class UsageType(models.TextChoices):
        YANDEX = 'YANDEX', 'Yandex Taxi'
        ONAY = 'ONAY', 'Onay Public Transport'
        BILLING = 'BILLING', 'Utility Billing'
        PRIVATE_CAR = 'PRIVATE_CAR', 'Private Car'
        OTHER = 'OTHER', 'Other'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='usage_logs')
    date = models.DateField()
    usage_type = models.CharField(max_length=20, choices=UsageType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in km or kWh")
    co2_emitted = models.DecimalField(max_digits=10, decimal_places=4)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.usage_type} - {self.date}"

class ConversionRate(models.Model):
    year = models.IntegerField(unique=True)
    co2_per_tree = models.DecimalField(max_digits=10, decimal_places=4, help_text="CO2 tonnes offset by one tree in this year")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.year}: {self.co2_per_tree} tonnes/tree"
