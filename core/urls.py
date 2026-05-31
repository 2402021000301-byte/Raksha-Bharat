"""Core App - API URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationViewSet

router = DefaultRouter()
router.register(r'users', UserRegistrationViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
