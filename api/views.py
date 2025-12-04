from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg
from django.shortcuts import get_object_or_404
from ledger.models import CarbonLedger
from planting.models import TreeTransaction, PlantingVerification
from accounts.models import FriendRequest, District, Company, MLPrediction
from .serializers import (
    UserSerializer, CarbonLedgerSerializer, TreeTransactionSerializer,
    PlantingVerificationSerializer, ConvertSerializer,
    FriendRequestSerializer, DistrictSerializer, CompanySerializer, MLPredictionSerializer
)
import random

User = get_user_model()

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def friends(self, request):
        friends = request.user.friends.all()
        serializer = self.get_serializer(friends, many=True)
        return Response(serializer.data)

class FriendRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, status='PENDING')

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        friend_request = self.get_object()
        if friend_request.to_user != request.user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        friend_request.status = 'ACCEPTED'
        friend_request.save()
        
        # Add to friends list (both ways)
        request.user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(request.user)
        
        return Response({"status": "accepted"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        friend_request = self.get_object()
        if friend_request.to_user != request.user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        friend_request.status = 'REJECTED'
        friend_request.save()
        return Response({"status": "rejected"})

class LeaderboardView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Top Users (by lowest carbon score, assuming lower is better, or higher is better? 
        # Requirement says "Greenest". Usually means lower emissions or higher "Green Score".
        # Let's assume higher "Green Score" is better.
        top_users = User.objects.order_by('-current_carbon_score')[:10]
        top_companies = Company.objects.order_by('-green_score')[:10]
        top_districts = District.objects.order_by('-green_score')[:10]

        return Response({
            'users': UserSerializer(top_users, many=True).data,
            'companies': CompanySerializer(top_companies, many=True).data,
            'districts': DistrictSerializer(top_districts, many=True).data
        })

class MLPredictionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Check if prediction exists for today (or just latest)
        prediction = MLPrediction.objects.filter(user=request.user).order_by('-created_at').first()
        
        if not prediction:
            # Generate mock prediction
            predicted_debt = random.uniform(1000, 5000)
            actions = [
                "Switch to public transport for 3 days a week.",
                "Install smart thermostat to reduce heating costs.",
                "Plant 5 more trees to offset current usage.",
                "Reduce air travel by 20% this year."
            ]
            recommended_action = random.choice(actions)
            
            prediction = MLPrediction.objects.create(
                user=request.user,
                predicted_year_end_debt=round(predicted_debt, 2),
                recommended_action=recommended_action,
                confidence_score=0.85
            )
        
        return Response(MLPredictionSerializer(prediction).data)

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
