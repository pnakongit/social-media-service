from django.urls import path
from knox.views import LogoutAllView

from account.views import UserCreateApiView, LoginApiView, LogoutView

urlpatterns = [
    path("register/", UserCreateApiView.as_view(), name="user_create"),
    path("login/", LoginApiView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("logout-all/", LogoutAllView.as_view(), name="logout_all"),
]

app_name = "account"
