from django.urls import path
from user.views import (
    RegisterUserView,
    RegisterManagerView,
    RegisterAdminView,
    Updateview,
    GetUserview,
)

app_name = "user"
urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register_user"),
    path("register/manager/", RegisterManagerView.as_view(), name="register_manager"),
    path("register/admin/", RegisterAdminView.as_view(), name="register_admin"),
    path("admin/", Updateview.as_view(), name="admin"),
    path("user/", GetUserview.as_view(), name="userchecking"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", UserProfileView.as_view, name="profile"),
]
