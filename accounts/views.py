from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, get_user_model
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from .forms import LoginForm, RegisterForm, UserForm, ProfileForm
from accounts.models import Profile
from django.contrib import messages
from django.db.models import Q, Prefetch, Sum, F, ExpressionWrapper, DurationField
from portfolio.models import ProjectImage, Project, Skill
from core.models import Activity
from django.core.paginator import Paginator
from django.db.models.functions import Replace

User = get_user_model()


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
    is_fresh_bot_redirect = request.session.pop("bot_filters_fresh", False)
    is_pagination = "page" in request.GET

    if not is_fresh_bot_redirect and not is_pagination:
        if "bot_filters" in request.session:
            del request.session["bot_filters"]
            request.session.modified = True

    query = request.GET.get("q", "").strip()
    availability = request.GET.get("availability", "").strip()

    bot_filters = request.session.get("bot_filters", {})

    skills_list = bot_filters.get("skills", [])
    roles_list = bot_filters.get("role", [])
    exp_query = bot_filters.get("exp")
    bot_q_query = bot_filters.get("q")

    devs = Profile.objects.select_related("user").prefetch_related(
        "skills", "experiences"
    )

    search_term = query or bot_q_query
    if search_term:
        devs = devs.filter(
            Q(user__username__icontains=search_term)
            | Q(user__first_name__icontains=search_term)
            | Q(user__last_name__icontains=search_term)
            | Q(jop_title__icontains=search_term)
        )

    if availability == "available":
        devs = devs.filter(available_for_work=True)

    if skills_list and len(skills_list) > 0:
        skill_conditions = Q()
        for skill in skills_list:
            if skill:
                skill_conditions |= Q(skills__name__icontains=skill)
        devs = devs.filter(skill_conditions)

    if roles_list and len(roles_list) > 0:
        role_conditions = Q()
        for role in roles_list:
            if role:
                role_clean = role.lower().strip()

                role_conditions |= Q(jop_title__icontains=role_clean)

                words = role_clean.replace("-", " ").split()

                ignore_words = [
                    "developer",
                    "engineer",
                    "مطور",
                    "مبرمج",
                    "مهندس",
                    "specialist",
                ]

                meaningful_words = [
                    w for w in words if w not in ignore_words and len(w) > 2
                ]

                if meaningful_words:
                    word_q = Q()
                    for word in meaningful_words:
                        word_q |= Q(jop_title__icontains=word)

                    role_conditions |= word_q

        devs = devs.filter(role_conditions)

    if exp_query:
        try:
            target_years = int(exp_query)
            target_days = target_years * 365.25
            current_date = timezone.now().date()

            devs = devs.annotate(
                total_experience=Sum(
                    ExpressionWrapper(
                        Coalesce(F("experiences__end_date"), current_date)
                        - F("experiences__start_date"),
                        output_field=DurationField(),
                    )
                )
            ).filter(total_experience__gte=timedelta(days=target_days))
        except (ValueError, TypeError):
            pass

    devs = devs.distinct()

    paginator = Paginator(devs, 9)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "accounts/developers.html",
        {
            "page_obj": page_obj,
            "query": query,
            "availability": availability,
            "has_bot_filters": bool(bot_filters and any(bot_filters.values())),
        },
    )


def developer_detail_view(request, username):
    user = get_object_or_404(
        User,
        username__iexact=username,
    )
    if user == request.user:
        if not hasattr(user, "profile"):
            return redirect("accounts:create_profile")

    developer = get_object_or_404(
        Profile.objects.select_related("user").prefetch_related(
            "skills",
            "experiences",
            "educations",
            Prefetch(
                "projects",
                queryset=(
                    Project.objects.order_by("-created_at")
                    .prefetch_related(
                        Prefetch(
                            "images",
                            queryset=ProjectImage.objects.order_by("display_order")[:1],
                            to_attr="cover_images",
                        )
                    )
                    .filter(is_featured=True)[:2]
                ),
                to_attr="preview_projects",
            ),
        ),
        user=user,
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

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.CREATED,
                target=profile,
            )

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

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.UPDATED,
                target=profile,
            )

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
