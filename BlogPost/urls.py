from django.urls import path
from .views import (
    blogpost_view,
    blogpost_details_view,
    add_comment_view,
    edit_comment_view,
    delete_comment_view,
)

app_name = "blog"


urlpatterns = [
    # Blog urls
    path(
        "blogs/",
        blogpost_view,
        name="blogs",
    ),
    path(
        "blog-details/<str:slug>/",
        blogpost_details_view,
        name="blog_details",
    ),
    # Comment urls
    path(
        "blog/add-comment/<str:blog_slug>/",
        add_comment_view,
        name="add_comment",
    ),
    path(
        "blog/<slug:blog_slug>/comment/<int:comment_id>/edit/",
        edit_comment_view,
        name="edit_comment",
    ),
    path(
        "blog/comment/<int:pk>/delete/",
        delete_comment_view,
        name="delete_comment",
    ),
]
