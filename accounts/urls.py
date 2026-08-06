from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("regester/", admin.site.urls, name="regester"),
]
