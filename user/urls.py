from django.urls import path
from user.views import (
    RegisterUserView,
    RegisterManagerView,
    RegisterAdminView,
)

app_name = "user"
urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register_user"),
    path("register/manager/",  RegisterManagerView.as_view(), name="register_manager"),
    path("register/admin/", RegisterAdminView.as_view(), name="register_admin"),
]
