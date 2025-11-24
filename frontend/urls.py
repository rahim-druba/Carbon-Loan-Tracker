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

    # Agent
    path('agent/queue/', views.agent_queue, name='agent_queue'),
    path('agent/verify/<int:transaction_id>/', views.verify_planting, name='verify_planting'),
]
