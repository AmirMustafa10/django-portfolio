from django.contrib import admin
from django.urls import path
from .views import login_view, register_view, logout_view, developers_view, developer_detail_view

app_name = "accounts"


urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("developers/", developers_view, name="developers"),
    path("developer/<str:username>/", developer_detail_view, name="developer_detail"),
]
