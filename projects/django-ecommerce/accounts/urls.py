"""
URL configuration for the accounts app.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/detail/', views.UserProfileDetailView.as_view(), name='profile_detail'),
    path('dashboard/', views.user_dashboard_view, name='dashboard'),
    
    # Addresses
    path('addresses/', views.AddressListView.as_view(), name='address_list'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address_detail'),
    
    # Password Management
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
