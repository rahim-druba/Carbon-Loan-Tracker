from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Vehicle, OnayCard, Property

class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'role', 'date_of_birth', 'city', 'national_id', 'national_id_card_photo', 'phone_number', 'avatar')

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['license_plate', 'make_model', 'fuel_type']

class OnayCardForm(forms.ModelForm):
    class Meta:
        model = OnayCard
        fields = ['card_number']

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['address', 'area_sqm', 'heating_type']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'city', 'phone_number', 'avatar', 'date_of_birth', 'national_id']
