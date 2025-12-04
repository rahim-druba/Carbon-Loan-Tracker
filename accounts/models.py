from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class District(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    green_score = models.FloatField(default=0.0) # Collective score

    def __str__(self):
        return f"{self.name}, {self.city}"

class Company(models.Model):
    name = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    green_score = models.FloatField(default=0.0) # Corporate score

    def __str__(self):
        return self.name

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
    
    # Social & Gamification
    friends = models.ManyToManyField('self', blank=True)
    current_carbon_score = models.FloatField(default=500.0) # Start with a neutral score
    
    # Demographics for Analytics
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='residents')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')

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

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected')], default='PENDING')

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"

class MLPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    predicted_year_end_debt = models.FloatField(help_text="Predicted carbon debt in kgCO2")
    recommended_action = models.TextField(help_text="AI suggested action to reduce debt")
    confidence_score = models.FloatField(default=0.85, help_text="Mock confidence score")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction for {self.user} at {self.created_at}"
