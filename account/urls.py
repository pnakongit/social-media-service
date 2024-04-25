from django.urls import path

from account.views import UserCreateApiView

urlpatterns = [
    path("register/", UserCreateApiView.as_view(), name="user_create"),
]

app_name = "account"
