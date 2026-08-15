from messaging.models import Message


def unread_messages(request):
    if not request.user.is_authenticated:
        return {
            "unread_messages_count": 0,
        }

    return {
        "unread_messages_count": Message.objects.filter(
            receiver=request.user,
            is_read=False,
        ).count(),
    }
