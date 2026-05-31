"""Core App Models - User Authentication & Profile Management
Government Grade Security Implementation
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator
from django.utils import timezone
from django.core.encryption import get_random_string
import uuid
import hashlib

class CustomUser(AbstractUser):
    """
    Custom User Model with Government Grade Fields
    Extends Django's AbstractUser with additional security and verification features
    """
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('police', 'Police Officer'),
        ('admin', 'Administrator'),
        ('ngo', 'NGO'),
        ('volunteer', 'Volunteer'),
        ('medical', 'Medical Professional'),
        ('government', 'Government Officer'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    STATE_CHOICES = [
        ('AP', 'Andhra Pradesh'),
        ('AR', 'Arunachal Pradesh'),
        ('AS', 'Assam'),
        ('BR', 'Bihar'),
        ('CG', 'Chhattisgarh'),
        ('GA', 'Goa'),
        ('GJ', 'Gujarat'),
        ('HR', 'Haryana'),
        ('HP', 'Himachal Pradesh'),
        ('JK', 'Jammu and Kashmir'),
        ('JH', 'Jharkhand'),
        ('KA', 'Karnataka'),
        ('KL', 'Kerala'),
        ('MP', 'Madhya Pradesh'),
        ('MH', 'Maharashtra'),
        ('MN', 'Manipur'),
        ('ML', 'Meghalaya'),
        ('MZ', 'Mizoram'),
        ('NL', 'Nagaland'),
        ('OD', 'Odisha'),
        ('PB', 'Punjab'),
        ('RJ', 'Rajasthan'),
        ('SK', 'Sikkim'),
        ('TN', 'Tamil Nadu'),
        ('TR', 'Telangana'),
        ('UP', 'Uttar Pradesh'),
        ('UK', 'Uttarakhand'),
        ('WB', 'West Bengal'),
    ]
    
    # Unique Identifiers
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True, unique=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True, unique=True)
    
    # User Profile Information
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Address Information
    country = models.CharField(max_length=100, default='India')
    state = models.CharField(max_length=2, choices=STATE_CHOICES, blank=True)
    city = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    address = models.TextField(blank=True)
    
    # Location (for GPS tracking)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    last_location_update = models.DateTimeField(blank=True, null=True)
    
    # Verification Status
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    document_verified = models.BooleanField(default=False)
    
    # Profile Information
    profile_picture = models.ImageField(
        upload_to='profile_pictures/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    bio = models.TextField(blank=True, max_length=500)
    
    # Emergency Contacts (JSON format)
    emergency_contacts = models.JSONField(default=list, blank=True, help_text="List of emergency contacts")
    
    # Safety Features
    enable_sos = models.BooleanField(default=True, help_text="Enable SOS emergency feature")
    enable_location_sharing = models.BooleanField(default=True)
    enable_notifications = models.BooleanField(default=True)
    
    # Account Security
    two_factor_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    is_government_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_login_device = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'custom_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uid']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    def get_full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def has_verified_profile(self):
        """Check if user profile is fully verified"""
        return self.email_verified and self.phone_verified
    
    def update_location(self, latitude, longitude):
        """Update user's current location"""
        self.latitude = latitude
        self.longitude = longitude
        self.last_location_update = timezone.now()
        self.save()


class OTP(models.Model):
    """
    One-Time Password Model for secure verification
    """
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('2fa', 'Two Factor Authentication'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    recipient = models.CharField(max_length=255)  # Email or phone number
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'otps'
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.user.username} ({self.type})"
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and timezone.now() <= self.expires_at
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def verify(self, code):
        """Verify OTP code"""
        if self.is_used or self.is_expired():
            return False
        
        self.attempts += 1
        if self.attempts > 3:
            return False
        
        if self.code == code:
            self.is_used = True
            self.verified_at = timezone.now()
            self.save()
            return True
        
        self.save()
        return False


class AuditLog(models.Model):
    """
    Audit Log for tracking user actions and security events
    Government compliance requirement
    """
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('password_change', 'Password Changed'),
        ('profile_update', 'Profile Updated'),
        ('report_filed', 'Report Filed'),
        ('document_uploaded', 'Document Uploaded'),
        ('location_shared', 'Location Shared'),
        ('sos_activated', 'SOS Activated'),
        ('admin_action', 'Admin Action'),
        ('security_event', 'Security Event'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('success', 'Success'), ('failure', 'Failure')])
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"


class UserDevice(models.Model):
    """
    Track user devices for security and multi-device support
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=255, unique=True)
    device_name = models.CharField(max_length=255)
    device_type = models.CharField(max_length=50, choices=[
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('desktop', 'Desktop'),
        ('web', 'Web Browser'),
    ])
    os = models.CharField(max_length=50)
    browser = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    is_trusted = models.BooleanField(default=False)
    last_used = models.DateTimeField(auto_now=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_devices'
        verbose_name = 'User Device'
        verbose_name_plural = 'User Devices'
        unique_together = ('user', 'device_id')
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name}"
