from django.urls import path
from .views import home, dashboard_view, activity_view

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("activity/", activity_view, name="activity"),
]
