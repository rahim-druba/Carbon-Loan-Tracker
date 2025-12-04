from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Sum
from ledger.models import CarbonLedger
from planting.models import TreeTransaction, PlantingVerification
from .serializers import (
    UserSerializer, CarbonLedgerSerializer, TreeTransactionSerializer,
    PlantingVerificationSerializer, ConvertSerializer
)

User = get_user_model()

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class LedgerViewSet(viewsets.ModelViewSet):
    serializer_class = CarbonLedgerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_agent():
            return CarbonLedger.objects.all()
        return CarbonLedger.objects.filter(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TreeTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_agent():
            return TreeTransaction.objects.all()
        return TreeTransaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PlantingVerificationViewSet(viewsets.ModelViewSet):
    queryset = PlantingVerification.objects.all()
    serializer_class = PlantingVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(agent=self.request.user)

class ConvertView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ConvertSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StatsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total_co2 = CarbonLedger.objects.aggregate(Sum('total_co2_tonnes'))['total_co2_tonnes__sum'] or 0
        total_trees = TreeTransaction.objects.filter(status='APPROVED').aggregate(Sum('quantity'))['quantity__sum'] or 0
        pending_verifications = PlantingVerification.objects.filter(is_verified=False).count()
        
        return Response({
            'total_co2_tonnes': total_co2,
            'total_trees_planted': total_trees,
            'pending_verifications': pending_verifications
        })
