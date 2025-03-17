from rest_framework import permissions
from rest_framework.permissions import BasePermission


class AdminUser(permissions.BasePermission):
    """
    Faqat admin (superuser) bo'lgan foydalanuvchilarga ruxsat beradi.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsAdminOrReadOnly(BasePermission):
    """
    Agar foydalanuvchi admin bo‘lsa, barcha ruxsat beriladi.
    Oddiy foydalanuvchilar faqat GET (ko‘rish) imkoniyatiga ega.
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True  # Hamma ko‘ra oladi
        return request.user and request.user.is_staff  

class IsAuthenticatedUser(permissions.BasePermission):
    """
    Faqat autentifikatsiya qilingan foydalanuvchilarga ruxsat beradi.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Agar foydalanuvchi o‘z ma’lumotlariga kirmoqchi bo‘lsa, ruxsat beriladi.
    Boshqalar faqat o‘qish huquqiga ega bo‘ladi.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class AllowAny(permissions.BasePermission):
    """
    Har qanday foydalanuvchiga ruxsat beradi (autentifikatsiya shart emas).
    """
    def has_permission(self, request, view):
        return True

from rest_framework.permissions import BasePermission

class IsTeacher(BasePermission):
    """Faqat o‘qituvchilar uchun ruxsat"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_teacher


class IsStudent(BasePermission):
    """Faqat studentlar faqat o‘qish huquqiga ega"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_student

    def has_object_permission(self, request, view, obj):
        return request.method in ["GET", "HEAD", "OPTIONS"]
