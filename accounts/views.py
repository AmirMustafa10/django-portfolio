from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .forms import LoginForm, RegisterForm, UserForm, ProfileForm
from accounts.models import Profile
from django.contrib import messages
from django.db.models import Q, Prefetch
from portfolio.models import ProjectImage, Project, Skill


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
                    )[:2]
                ),
                to_attr="preview_projects",
            ),
        ),
        user__username__iexact=username,
    )

    projects_count = developer.projects.count()  # type: ignore

    return render(
        request,
        "accounts/developer_detail.html",
        {
            "developer": developer,
            "projects_count": projects_count,
        },
    )


@login_required
def create_profile_view(request):
    user = request.user

    skills = Skill.objects.all()

    if hasattr(user, "profile"):
        return redirect(
            "accounts:developer_detail",
            username=user.username,
        )

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        user_form = UserForm(request.POST, instance=user)

        if form.is_valid() and user_form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            user_form.save()

            selected_skill_values = request.POST.getlist("skills")
            new_skill_names = request.POST.getlist("new_skills")

            selected_skill_ids = []

            for value in selected_skill_values:

                if not value.startswith("new-"):
                    selected_skill_ids.append(value)

            for skill_name in new_skill_names:
                skill_name = skill_name.strip().title()

                if not skill_name:
                    continue

                skill, created = Skill.objects.get_or_create(name=skill_name)

                selected_skill_ids.append(skill.id)  # type: ignore

            profile.skills.set(selected_skill_ids)

            messages.success(
                request,
                "Profile created successfully.",
            )

            return redirect(
                "accounts:developer_detail",
                username=user.username,
            )

    else:
        form = ProfileForm()
        user_form = UserForm(instance=user)

    return render(
        request,
        "accounts/create_profile.html",
        {
            "profile_form": form,
            "user_form": user_form,
            "skills": skills,
        },
    )


@login_required
def edit_profile_view(request):

    user = request.user
    profile = user.profile
    skills = Skill.objects.all()
    selected_skills = profile.skills.all()
    experiences = profile.experiences.all()
    educations = profile.educations.all()

    if request.method == "POST":
        form1 = UserForm(request.POST, instance=user)
        form2 = ProfileForm(request.POST, request.FILES, instance=profile)

        selected_skill_values = request.POST.getlist("skills")

        if form1.is_valid() and form2.is_valid():

            form1.save()
            form2.save()

            selected_skill_values = request.POST.getlist("skills")
            new_skill_names = request.POST.getlist("new_skills")

            selected_skill_ids = []

            for value in selected_skill_values:

                if not value.startswith("new-"):
                    selected_skill_ids.append(value)

            for skill_name in new_skill_names:
                skill_name = skill_name.strip().title()

                if not skill_name:
                    continue

                skill, created = Skill.objects.get_or_create(name=skill_name)

                selected_skill_ids.append(skill.id)  # type: ignore

            profile.skills.set(selected_skill_ids)

            return redirect(
                "accounts:developer_detail",
                username=user.username,
            )

    else:
        form1 = UserForm(instance=user)
        form2 = ProfileForm(instance=profile)

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "user_form": form1,
            "profile_form": form2,
            "skills": skills,
            "selected_skills": selected_skills,
            "experiences": experiences,
            "educations": educations,
        },
    )
