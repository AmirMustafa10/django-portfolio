from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, logout
from .forms import LoginForm, RegisterForm
from accounts.models import Profile
from django.db.models import Q, Prefetch
from portfolio.models import ProjectImage, Project


def register_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect("home")

    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect("home")

    else:
        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )


def logout_view(request):
    logout(request)

    return redirect("home")


def developers_view(request):

    query = request.GET.get("q", "").strip()
    availability = request.GET.get("availability", "").strip()

    devs = Profile.objects.select_related("user").prefetch_related("skills")

    if query:
        devs = devs.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
        )

    if availability == "available":
        devs = devs.filter(available_for_work=True)

    devs = devs.distinct()

    return render(
        request,
        "accounts/developers.html",
        {
            "developers": devs,
            "query": query,
            "availability": availability,
        },
    )


def developer_detail_view(request, username):

    developer = get_object_or_404(
        Profile.objects.select_related("user").prefetch_related(
            "skills",
            "experiences",
            "educations",
            Prefetch(
                "projects",
                queryset=(
                    Project.objects.order_by("-created_at").prefetch_related(
                        Prefetch(
                            "images",
                            queryset=ProjectImage.objects.order_by("display_order")[:1],
                            to_attr="cover_images",
                        )
                    )[:3]
                ),
                to_attr="preview_projects",
            ),
        ),
        user__username__iexact=username,
    )

    projects_count = developer.projects.count() # type: ignore

    return render(
        request,
        "accounts/developer_detail.html",
        {
            "developer": developer,
            "projects_count": projects_count,
        },
    )
