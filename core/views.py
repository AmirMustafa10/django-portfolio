from django.shortcuts import render
from accounts.models import Profile
from django.db.models import Count


def home(request):

    developers = (
        Profile.objects.select_related("user")
        .prefetch_related("skills")
        .annotate(
            projects_count=Count("projects", distinct=True),
        )[:6]
    )

    return render(
        request,
        "home.html",
        {
            "developers": developers,
        },
    )
