from rest_framework.permissions import SAFE_METHODS,BasePermission,IsAuthenticated
from django.contrib.auth import get_user_model



User = get_user_model()

class IsAdminorReadonly(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.Is_Admin_role
    
class IsUser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.Is_User_role    
