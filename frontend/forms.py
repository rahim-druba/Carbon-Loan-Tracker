from django import forms
from planting.models import TreeTransaction, PlantingVerification

class ConvertForm(forms.Form):
    public_transport_km = forms.FloatField(min_value=0, initial=0, label="Public Transport (km)")
    ride_hailing_km = forms.FloatField(min_value=0, initial=0, label="Ride Hailing (km)")
    private_vehicle_km = forms.FloatField(min_value=0, initial=0, label="Private Vehicle (km)")
    electricity_kwh = forms.FloatField(min_value=0, initial=0, label="Electricity (kWh)")
    heating_kwh = forms.FloatField(min_value=0, initial=0, label="Heating (kWh)")

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = TreeTransaction
        fields = ['quantity', 'payment_reference']

class VerificationForm(forms.ModelForm):
    class Meta:
        model = PlantingVerification
        fields = ['image_proof', 'location', 'planted_at']
        widgets = {
            'planted_at': forms.DateInput(attrs={'type': 'datetime-local'}),
        }
