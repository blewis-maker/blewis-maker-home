"""
Views for the accounts app.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import User, UserProfile, Address
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, UserProfileDetailSerializer, AddressSerializer,
    PasswordChangeSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Create a new user and return JWT tokens.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(TokenObtainPairView):
    """
    User login endpoint with custom response.
    """
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        """
        Login user and return JWT tokens with user data.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful'
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Get and update detailed user profile.
    """
    serializer_class = UserProfileDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class AddressListView(generics.ListCreateAPIView):
    """
    List and create user addresses.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-is_default', '-created_at')


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific address.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class PasswordChangeView(APIView):
    """
    Change user password.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Change user password.
        """
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """
    Request password reset.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Send password reset email.
        """
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Generate reset token
            reset_token = get_random_string(32)
            user.reset_token = reset_token
            user.reset_token_expires = timezone.now() + timedelta(hours=1)
            user.save()
            
            # Send reset email
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({'message': 'Password reset email sent'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Reset password with token.
        """
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(reset_token=token)
            if user.reset_token_expires < timezone.now():
                return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.reset_token = None
            user.reset_token_expires = None
            user.save()
            return Response({'message': 'Password reset successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout user by blacklisting the refresh token.
    """
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'})
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_view(request):
    """
    Get user dashboard data.
    """
    user = request.user
    
    # Get user's recent orders
    recent_orders = user.orders.all()[:5]
    
    # Get user's addresses
    addresses = Address.objects.filter(user=user)[:3]
    
    # Get user's wishlist items
    wishlist_items = user.wishlist.all()[:5]
    
    return Response({
        'user': UserProfileSerializer(user).data,
        'recent_orders': [
            {
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at
            } for order in recent_orders
        ],
        'addresses': AddressSerializer(addresses, many=True).data,
        'wishlist_count': user.wishlist.count(),
        'orders_count': user.orders.count()
    })