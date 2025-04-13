from rest_framework.permissions import SAFE_METHODS,BasePermission
from user.models import UserAccount

class IsAdminorReadonly(BasePermission):

    def AdminPermissions(self , view , request):
        get_data = UserAccount.get()
        if request.user.role == 'Admin':
            return SAFE_METHODS

