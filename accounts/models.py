from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        CITIZEN = 'CITIZEN', 'Citizen'
        AGENT = 'AGENT', 'Planting Agent'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CITIZEN)
    date_of_birth = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    national_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def is_citizen(self):
        return self.role == self.Role.CITIZEN

    def is_agent(self):
        return self.role == self.Role.AGENT

    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser
