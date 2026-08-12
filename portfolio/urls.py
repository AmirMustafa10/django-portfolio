from django.urls import path
from .views import (
    delete_experience_view,
    edit_experience_view,
    add_experience_view,
    delete_education_view,
    edit_education_view,
    add_education_view,
)

app_name = "portfolio"


urlpatterns = [
    path(
        "experience/<int:pk>/delete/",
        delete_experience_view,
        name="delete_experience",
    ),
    path(
        "edit_experience/<int:pk>/",
        edit_experience_view,
        name="edit_experience",
    ),
    path(
        "add_experience/",
        add_experience_view,
        name="add_experience",
    ),
    # Education Urls
    path(
        "delete_education/<int:pk>/delete/",
        delete_education_view,
        name="delete_education",
    ),
    path(
        "edit_education/<int:pk>/",
        edit_education_view,
        name="edit_education",
    ),
    path(
        "add_education/",
        add_education_view,
        name="add_education",
    ),
]
