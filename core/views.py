"""Core App - Views for Authentication"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import JsonResponse
from datetime import timedelta
import random
import string
from .models import OTP, AuditLog, UserDevice
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer,
    OTPSerializer, AuditLogSerializer, UserDeviceSerializer
)

User = get_user_model()

class UserRegistrationViewSet(viewsets.ModelViewSet):
    """
    User Registration and Authentication ViewSet
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        Register a new user and send OTP
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate and send OTP
            otp_code = ''.join(random.choices(string.digits, k=6))
            OTP.objects.create(
                user=user,
                code=otp_code,
                type='email',
                recipient=user.email,
                expires_at=timezone.now() + timedelta(minutes=5)
            )
            
            # Send OTP email
            try:
                send_mail(
                    'Raksha Bharat - Email Verification OTP',
                    f'Your OTP for email verification is: {otp_code}\nValid for 5 minutes.',
                    'noreply@raksha-bharat.gov.in',
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Email sending failed: {str(e)}")
            
            # Log audit
            AuditLog.objects.create(
                user=user,
                action='login',
                ip_address=self.get_client_ip(request),
                status='success',
                description='New user registration'
            )
            
            return Response({
                'status': 'success',
                'message': 'User registered successfully. OTP sent to email.',
                'user_id': user.uid
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify_otp(self, request):
        """
        Verify OTP and confirm email
        """
        email = request.data.get('email')
        code = request.data.get('code')
        
        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.filter(user=user, type='email', recipient=email).latest('created_at')
            
            if otp.verify(code):
                user.email_verified = True
                user.save()
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                AuditLog.objects.create(
                    user=user,
                    action='login',
                    ip_address=self.get_client_ip(request),
                    status='success',
                    description='Email verified and logged in'
                )
                
                return Response({
                    'status': 'success',
                    'message': 'Email verified successfully',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserProfileSerializer(user).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Invalid OTP'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except OTP.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'OTP not found or expired'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        User Logout
        """
        AuditLog.objects.create(
            user=request.user,
            action='logout',
            ip_address=self.get_client_ip(request),
            status='success'
        )
        
        return Response({
            'status': 'success',
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """
        Get user profile
        """
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        Update user profile
        """
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='profile_update',
                ip_address=self.get_client_ip(request),
                status='success'
            )
            
            return Response({
                'status': 'success',
                'message': 'Profile updated successfully',
                'user': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Change user password
        """
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not request.user.check_password(old_password):
            return Response({
                'status': 'error',
                'message': 'Old password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({
                'status': 'error',
                'message': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 12:
            return Response({
                'status': 'error',
                'message': 'Password must be at least 12 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.set_password(new_password)
        request.user.save()
        
        AuditLog.objects.create(
            user=request.user,
            action='password_change',
            ip_address=self.get_client_ip(request),
            status='success'
        )
        
        return Response({
            'status': 'success',
            'message': 'Password changed successfully'
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def audit_logs(self, request):
        """
        Get user's audit logs
        """
        logs = AuditLog.objects.filter(user=request.user).order_by('-timestamp')[:50]
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def devices(self, request):
        """
        Get user's trusted devices
        """
        devices = UserDevice.objects.filter(user=request.user)
        serializer = UserDeviceSerializer(devices, many=True)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# Error handling views
def error_404(request, exception=None):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)
