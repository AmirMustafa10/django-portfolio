from django.urls import path
from .views import messages_view, conversation_view

app_name = "messaging"


urlpatterns = [
    path("chats/", messages_view, name="messages"),
    path("conversation/<str:username>", conversation_view, name="conversation"),
]
