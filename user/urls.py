from django.urls import path
from user import views
urlpatterns = [
    path("register/", views.register_user, name="RegisterforNew user"),
    path("register/manager/",views.register_manager),
    path("register/admin/", views.register_admin),
]
