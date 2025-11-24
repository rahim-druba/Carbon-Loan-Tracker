from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import (
    UserViewSet, LedgerViewSet, TransactionViewSet, 
    PlantingVerificationViewSet, ConvertView, StatsView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'ledger', LedgerViewSet, basename='ledger')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'planting', PlantingVerificationViewSet, basename='planting')

urlpatterns = [
    path('', include(router.urls)),
    path('convert/', ConvertView.as_view(), name='convert'),
    path('stats/', StatsView.as_view(), name='stats'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
