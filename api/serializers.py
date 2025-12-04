from rest_framework import serializers
from django.contrib.auth import get_user_model
from ledger.models import CarbonLedger
from planting.models import TreeTransaction, PlantingVerification
from ledger.calculations import calculate_co2, calculate_required_trees

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'date_of_birth', 'city', 'national_id', 'avatar']
        read_only_fields = ['role']

class CarbonLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonLedger
        fields = '__all__'
        read_only_fields = ['user', 'total_co2_tonnes', 'required_trees', 'status']

class TreeTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeTransaction
        fields = '__all__'
        read_only_fields = ['user', 'status']

class PlantingVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantingVerification
        fields = '__all__'
        read_only_fields = ['approved_by', 'approved_at', 'is_verified']

class ConvertSerializer(serializers.Serializer):
    public_transport_km = serializers.FloatField(default=0)
    ride_hailing_km = serializers.FloatField(default=0)
    private_vehicle_km = serializers.FloatField(default=0)
    electricity_kwh = serializers.FloatField(default=0)
    heating_kwh = serializers.FloatField(default=0)

    def validate(self, data):
        data['total_co2'] = calculate_co2(data)
        data['required_trees'] = calculate_required_trees(data['total_co2'])
        return data
