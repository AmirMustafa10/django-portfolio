from django.shortcuts import render, get_object_or_404
from accounts.models import Profile
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .models import Activity
from django.core.paginator import Paginator
from BlogPost.models import BlogPost
from portfolio.models import Project


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


@login_required
def dashboard_view(request):
    profile = get_object_or_404(
        Profile.objects.select_related("user"),
        user=request.user,
    )

    projects = Project.objects.filter(profile=profile).order_by("-updated_at")[:4]

    blogs = BlogPost.objects.filter(profile=profile).order_by("-updated_at")[:4]

    recent_activities = (
        Activity.objects.filter(user=request.user)
        .select_related("target_content_type")
        .order_by("-created_at")[:5]
    )

    stats = {
        "projects_count": Project.objects.filter(profile=profile).count(),
        "published_blogs_count": BlogPost.objects.filter(
            profile=profile,
            status=BlogPost.Status.PUBLISHED,
        ).count(),
        "draft_blogs_count": BlogPost.objects.filter(
            profile=profile,
            status=BlogPost.Status.DRAFT,
        ).count(),
        "skills_count": profile.skills.count(),
    }

    return render(
        request,
        "core/dashboard.html",
        {
            "profile": profile,
            "recent_projects": projects,
            "recent_blogs": blogs,
            "recent_activities": recent_activities,
            "stats": stats,
        },
    )


@login_required
def activity_view(request):
    activities = (
        Activity.objects.filter(user=request.user)
        .select_related("target_content_type")
        .order_by("-created_at")
    )

    paginator = Paginator(activities, 10)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "core/activity.html",
        {
            "page_obj": page_obj,
        },
    )
