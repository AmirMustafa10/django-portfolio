from django.urls import path
from .views import (
    delete_experience_view,
    edit_experience_view,
    add_experience_view,
    delete_education_view,
    edit_education_view,
    add_education_view,
    projects_view,
    project_details,
    my_projects_view,
    add_project_view,
    edit_project_view,
    delete_project_view,
    manage_project_images_view,
    delete_project_image_view,
    edit_project_image_caption_view,
)

app_name = "portfolio"


urlpatterns = [
    # Experience Urls
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
    # Project Urls
    path(
        "projects/",
        projects_view,
        name="projects",
    ),
    path(
        "project_details/<str:slug>/",
        project_details,
        name="project_details",
    ),
    path(
        "my-projects/",
        my_projects_view,
        name="my_projects",
    ),
    path(
        "add-project/",
        add_project_view,
        name="add_project",
    ),
    path(
        "edit-project/<str:slug>/",
        edit_project_view,
        name="edit_project",
    ),
    path(
        "project/<slug:slug>/delete/",
        delete_project_view,
        name="delete_project",
    ),
    # project images urls
    path(
        "manage-project-images/<str:slug>/",
        manage_project_images_view,
        name="manage_project_images",
    ),
    path(
        "delete-project-image/<int:pk>/delete/",
        delete_project_image_view,
        name="delete_project_image",
    ),
    path(
        "edit-project-image-caption/<int:pk>/delete/",
        edit_project_image_caption_view,
        name="edit_project_image_caption",
    ),
]
