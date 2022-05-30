from rest_framework.permissions import BasePermission

class ArticlePermissions(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['create', 'destroy']:
            return request.user.is_staff

        return True