from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        CITIZEN = 'CITIZEN', 'Citizen'
        AGENT = 'AGENT', 'Planting Agent'
        ADMIN = 'ADMIN', 'Admin'
        ANALYTICS = 'ANALYTICS', 'Analytics User'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CITIZEN)
    date_of_birth = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    national_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    national_id_card_photo = models.ImageField(upload_to='national_ids/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def is_citizen(self):
        return self.role == self.Role.CITIZEN

    def is_agent(self):
        return self.role == self.Role.AGENT

    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser
    
    def is_analytics(self):
        return self.role == self.Role.ANALYTICS

class Vehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    license_plate = models.CharField(max_length=20)
    make_model = models.CharField(max_length=100)
    fuel_type = models.CharField(max_length=50, choices=[('PETROL', 'Petrol'), ('DIESEL', 'Diesel'), ('ELECTRIC', 'Electric'), ('HYBRID', 'Hybrid')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.make_model} ({self.license_plate})"

class OnayCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='onay_cards')
    card_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.card_number

class Property(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    address = models.CharField(max_length=255)
    area_sqm = models.DecimalField(max_digits=10, decimal_places=2)
    heating_type = models.CharField(max_length=50, choices=[('GAS', 'Gas'), ('ELECTRIC', 'Electric'), ('CENTRAL', 'Central Heating')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
