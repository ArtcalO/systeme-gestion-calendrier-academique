from rest_framework.permissions import BasePermission


class IsAdminOrDean(BasePermission):
    """Réservé aux administrateurs et doyens"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'dean']


class IsSelfOrAdmin(BasePermission):
    """Soi-même ou un administrateur/doyen"""
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'dean']:
            return True
        return obj == request.user


class IsProfessor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'professor'


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'
