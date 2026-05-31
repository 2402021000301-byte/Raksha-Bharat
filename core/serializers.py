"""Core App - Serializers for API"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTP, AuditLog, UserDevice
import re

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12, required=True)
    password_confirm = serializers.CharField(write_only=True, min_length=12, required=True)
    phone_number = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone_number', 'first_name', 'last_name',
            'password', 'password_confirm', 'gender', 'date_of_birth',
            'state', 'city', 'pincode'
        ]
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Invalid phone number format")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered")
        return value
    
    def validate_email(self, value):
        """Validate email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered")
        return value
    
    def validate_username(self, value):
        """Validate username"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken")
        if len(value) < 4:
            raise serializers.ValidationError("Username must be at least 4 characters long")
        return value
    
    def validate(self, data):
        """Validate passwords match"""
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password'],
            gender=validated_data.get('gender', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            state=validated_data.get('state', ''),
            city=validated_data.get('city', ''),
            pincode=validated_data.get('pincode', ''),
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'uid', 'username', 'email', 'phone_number', 'first_name', 'last_name',
            'full_name', 'gender', 'date_of_birth', 'profile_picture', 'bio',
            'state', 'city', 'district', 'pincode', 'address',
            'role', 'email_verified', 'phone_verified', 'document_verified',
            'enable_sos', 'enable_location_sharing', 'enable_notifications',
            'is_government_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uid', 'email_verified', 'phone_verified', 'document_verified', 'is_government_verified', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['id', 'type', 'recipient', 'created_at', 'expires_at']
        read_only_fields = ['id', 'created_at', 'expires_at']

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['id', 'action', 'description', 'ip_address', 'status', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDevice
        fields = ['id', 'device_name', 'device_type', 'os', 'browser', 'ip_address', 'is_trusted', 'last_used']
        read_only_fields = ['id', 'last_used']
