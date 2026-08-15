from django.urls import path
from .views import (
    messages_view,
    conversation_view,
    send_message_view,
    delete_message_view,
    edit_message_view,
)

app_name = "messaging"


urlpatterns = [
    path("chats/", messages_view, name="messages"),
    path("conversation/<str:username>/", conversation_view, name="conversation"),
    path("send_message/<str:username>/", send_message_view, name="send_message"),
    path(
        "edit_message/<str:username>/<int:id>/", edit_message_view, name="edit_message"
    ),
    path("delete_message/<int:id>/delete/", delete_message_view, name="delete_message"),
]
