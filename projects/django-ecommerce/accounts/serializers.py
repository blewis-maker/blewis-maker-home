"""
Serializers for the accounts app.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, Address


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 
            'phone_number', 'date_of_birth', 'password', 'password_confirm'
        )
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        """
        Validate password confirmation.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        """
        Create a new user.
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        """
        Validate user credentials.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'phone_number', 'date_of_birth', 'is_verified',
            'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'email', 'is_verified', 'date_joined', 'last_login')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone_number', 'date_of_birth'
        )


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed user profile with extended information.
    """
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = (
            'id', 'user', 'avatar', 'bio', 'website', 'location', 
            'date_of_birth', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for user addresses.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Address
        fields = (
            'id', 'address_type', 'first_name', 'last_name', 'company',
            'address_line_1', 'address_line_2', 'city', 'state', 
            'postal_code', 'country', 'phone_number', 'is_default',
            'created_at', 'updated_at', 'full_name'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.full_name

    def create(self, validated_data):
        """
        Create a new address for the current user.
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate_old_password(self, value):
        """
        Validate old password.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

    def validate(self, attrs):
        """
        Validate password confirmation.
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs

    def save(self):
        """
        Change the user's password.
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Validate that the email exists.
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('No user found with this email address.')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    """
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        """
        Validate password confirmation.
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
