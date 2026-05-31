"""Core App - Admin Configuration"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, OTP, AuditLog, UserDevice

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Government Verification', {'fields': ('is_government_verified', 'verification_date')}),
        ('Profile Information', {
            'fields': (
                'uid', 'aadhaar_number', 'pan_number', 'gender', 'phone_number',
                'date_of_birth', 'profile_picture', 'bio'
            )
        }),
        ('Address Information', {
            'fields': ('country', 'state', 'city', 'district', 'pincode', 'address')
        }),
        ('Location', {'fields': ('latitude', 'longitude', 'last_location_update')}),
        ('Verification Status', {
            'fields': ('email_verified', 'phone_verified', 'document_verified')
        }),
        ('Safety Features', {
            'fields': (
                'enable_sos', 'enable_location_sharing', 'enable_notifications',
                'emergency_contacts'
            )
        }),
        ('Security', {'fields': ('two_factor_enabled', 'backup_codes')}),
        ('Login Information', {
            'fields': ('last_login_ip', 'last_login_device')
        }),
    )
    
    list_display = ('username', 'email', 'phone_number', 'role', 'is_government_verified', 'created_at')
    list_filter = ('role', 'is_government_verified', 'email_verified', 'phone_verified', 'created_at')
    search_fields = ('username', 'email', 'phone_number', 'uid')
    ordering = ('-created_at',)

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'recipient', 'is_used', 'created_at')
    list_filter = ('type', 'is_used', 'created_at')
    search_fields = ('user__username', 'recipient')
    readonly_fields = ('code', 'created_at', 'verified_at')
    ordering = ('-created_at',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'status', 'ip_address', 'timestamp')
    list_filter = ('action', 'status', 'timestamp')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action', 'ip_address')
    ordering = ('-timestamp',)

@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_name', 'device_type', 'ip_address', 'is_trusted', 'last_used')
    list_filter = ('device_type', 'os', 'is_trusted')
    search_fields = ('user__username', 'device_name', 'ip_address')
    readonly_fields = ('device_id', 'added_at', 'last_used')
    ordering = ('-last_used',)
