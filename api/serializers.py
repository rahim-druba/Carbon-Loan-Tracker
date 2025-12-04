from rest_framework import serializers
from django.contrib.auth import get_user_model
from ledger.models import CarbonLedger
from planting.models import TreeTransaction, PlantingVerification
from ledger.calculations import calculate_co2, calculate_required_trees
from accounts.models import District, Company, FriendRequest, MLPrediction

User = get_user_model()

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'date_of_birth', 'city', 'national_id', 'avatar', 'current_carbon_score', 'district', 'company']
        read_only_fields = ['role', 'current_carbon_score']

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)
    to_user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='to_user', write_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'to_user_id', 'created_at', 'status']
        read_only_fields = ['from_user', 'created_at', 'status']

class MLPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLPrediction
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

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
