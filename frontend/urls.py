from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', auth_views.LoginView.as_view(template_name='frontend/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Citizen
    path('ledger/', views.ledger_list, name='ledger_list'),
    path('ledger/<int:pk>/', views.ledger_detail, name='ledger_detail'),
    path('convert/', views.convert_carbon, name='convert_carbon'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('purchase/<int:ledger_id>/', views.purchase_trees, name='purchase_trees'),
    
    # Assets
    path('assets/', views.assets_list, name='assets_list'),
    path('assets/add/vehicle/', views.add_vehicle, name='add_vehicle'),
    path('assets/add/onay/', views.add_onay, name='add_onay'),
    path('assets/add/property/', views.add_property, name='add_property'),
    
    # Usage & Analytics
    path('usage/', views.usage_history, name='usage_history'),
    path('predictors/', views.predictors_hub, name='predictors_hub'),
    path('trip-planner/', views.trip_planner, name='trip_planner'),
    path('flight-planner/', views.flight_planner, name='flight_planner'),
    path('train-planner/', views.train_planner, name='train_planner'),
    path('analytics/citizen/', views.citizen_analytics, name='citizen_analytics'),
    
    # Analytics User / Admin
    path('analytics/dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/user/<int:user_id>/', views.analytics_user_detail, name='analytics_user_detail'),
    path('admin/config/', views.admin_config, name='admin_config'),

    # Agent
    path('agent/queue/', views.agent_queue, name='agent_queue'),
    path('agent/verify/<int:transaction_id>/', views.verify_planting, name='verify_planting'),
]
