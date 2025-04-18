from django.urls import path
from user.views import (
    RegisterUserView,
    RegisterManagerView,
    RegisterAdminView,
    LoginView,
    LogoutView,
    UserProfileView,
    ListMoviesonPerticularDate,
)

app_name = "user"
urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register_user"),
    path("register/manager/", RegisterManagerView.as_view(), name="register_manager"),
    path("register/admin/", RegisterAdminView.as_view(), name="register_admin"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", UserProfileView.as_view, name="profile"),
    path("showsbydate/",ListMoviesonPerticularDate.as_view(),name="showsbydate")
]
