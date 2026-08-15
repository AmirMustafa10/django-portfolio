from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef, Q, Subquery
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from .models import Message
from urllib.parse import urlparse
from django.contrib import messages
from .forms import MessageForm
from core.models import Activity

User = get_user_model()


@login_required
def messages_view(request):
    # Get messages exchanged between the current user and another user
    last_message = Message.objects.filter(
        Q(
            sender=OuterRef("pk"),  # The current user's ID from the outer User query
            receiver=request.user,
        )
        | Q(
            sender=request.user,
            receiver=OuterRef("pk"),
        )
    ).order_by("-created_at")

    # Check whether there are any messages between the current user and another user
    conversation_exists = Message.objects.filter(
        Q(
            sender=OuterRef("pk"),  # The current user's ID from the outer User query
            receiver=request.user,
        )
        | Q(
            sender=request.user,
            receiver=OuterRef("pk"),
        )
    )

    # Get users who have exchanged messages with the current user,
    # ordered by the time of their latest message
    users = (
        User.objects.exclude(pk=request.user.pk)  # get all users exclude me
        .annotate(
            last_message_at=Subquery(last_message.values("created_at")[:1]),
            has_conversation=Exists(conversation_exists),
            unread_count=Count(
                "sent_messages",
                filter=Q(
                    sent_messages__receiver=request.user,
                    sent_messages__is_read=False,
                ),
            ),
        )
        .filter(has_conversation=True)
        .order_by("-last_message_at")
    )

    paginator = Paginator(users, 10)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "messaging/messages.html",
        {
            "page_obj": page_obj,
        },
    )


@login_required
def conversation_view(request, username):
    other_user = get_object_or_404(
        User,
        username=username,
        is_active=True,
    )

    if other_user == request.user:
        messages.warning(
            request,
            ("You cannot send a message to yourself."),
        )
        return redirect("messaging:messages")

    # Mark incoming unread messages as read
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False,
    ).update(
        is_read=True,
        read_at=timezone.now(),
    )

    messages_qs = Message.objects.filter(
        Q(
            sender=other_user,
            receiver=request.user,
        )
        | Q(
            sender=request.user,
            receiver=other_user,
        )
    ).order_by("-created_at")

    paginator = Paginator(messages_qs, 10)

    page_number = request.GET.get("page", 1)

    page_obj = paginator.get_page(page_number)

    # Reverse only the current page for chat display
    chat_messages = list(page_obj.object_list)[::-1]

    return render(
        request,
        "messaging/conversation.html",
        {
            "page_obj": page_obj,
            "chat_messages": chat_messages,
            "other_user": other_user,
        },
    )


@login_required
def send_message_view(request, username):

    other_user = get_object_or_404(
        User,
        username=username,
        is_active=True,
    )

    if other_user == request.user:
        messages.warning(
            request,
            ("You cannot send a message to yourself."),
        )
        return redirect("messaging:messages")

    if request.method == "POST":
        form = MessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)

            message.sender = request.user
            message.receiver = other_user

            message.save()

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.CREATED,
                target=message,
            )

            return redirect(
                "messaging:conversation",
                username=other_user.username,
            )

    return redirect(
        "messaging:conversation",
        username=other_user.username,
    )


@login_required
def edit_message_view(request, username, id):
    message = get_object_or_404(
        Message,
        id=id,
        sender=request.user,
    )

    if request.method == "POST":
        form = MessageForm(
            request.POST,
            instance=message,
        )

        if form.is_valid():
            form.save()

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.UPDATED,
                target=message,
            )

            referer = request.META.get("HTTP_REFERER")

            if referer:
                parsed_referer = urlparse(referer)

                if parsed_referer.netloc == request.get_host():
                    return redirect(
                        parsed_referer.path
                        + (f"?{parsed_referer.query}" if parsed_referer.query else "")
                    )

    return redirect(
        "messaging:conversation",
        username=username,
    )


@login_required
def delete_message_view(request, id):
    message = get_object_or_404(
        Message,
        id=id,
        sender=request.user,
    )

    if request.method == "POST":
        message.delete()

        Activity.objects.create(
            user=request.user,
            action=Activity.Action.DELETED,
            target=message,
        )

        referer = request.META.get("HTTP_REFERER")

        if referer:
            parsed_referer = urlparse(referer)

            if parsed_referer.netloc == request.get_host():
                return redirect(
                    parsed_referer.path
                    + (f"?{parsed_referer.query}" if parsed_referer.query else "")
                )

    return HttpResponseNotAllowed(["POST"])
