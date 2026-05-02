from rest_framework.permissions import BasePermission
from rest_framework import permissions

class ArticlePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        # Permissions basées sur la méthode HTTP (plus fiable)
        if request.method == 'GET':
            return True

        if request.method == 'POST':
            return request.user.is_authenticated

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated and request.user.is_staff

        return False