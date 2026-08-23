from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from .models import Experience, Education, Project, Skill, ProjectImage
from .forms import EducationForm, ExperienceForm, ProjectForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from core.models import Activity


# Experience views
@login_required
def delete_experience_view(request, pk):
    experience = get_object_or_404(
        Experience,
        pk=pk,
        profile=request.user.profile,
    )

    if request.method == "POST":

        Activity.objects.create(
            user=request.user,
            action=Activity.Action.DELETED,
            target=experience,
        )

        experience.delete()

        messages.success(request, "Experience deleted successfully.")

        return redirect("accounts:edit_profile")

    return HttpResponseNotAllowed(["POST"])


@login_required
def edit_experience_view(request, pk):
    experience = get_object_or_404(
        Experience,
        pk=pk,
        profile=request.user.profile,
    )

    if request.method == "POST":
        form = ExperienceForm(request.POST, instance=experience)

        if form.is_valid():
            form.save()

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.UPDATED,
                target=experience,
            )

            messages.success(request, "Experience updated successfully.")

            return redirect("accounts:edit_profile")

    else:
        form = ExperienceForm(instance=experience)

    return render(
        request,
        "portfolio/experience/edit_experience.html",
        {
            "experience_form": form,
            "experience": experience,
        },
    )


@login_required
def add_experience_view(request):
    if request.method == "POST":
        form = ExperienceForm(request.POST)

        if form.is_valid():
            experience = form.save(commit=False)
            experience.profile = request.user.profile
            experience.save()

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.CREATED,
                target=experience,
            )

            messages.success(request, "Experience added successfully.")

            return redirect("accounts:edit_profile")

    else:
        form = ExperienceForm()

    return render(
        request,
        "portfolio/experience/add_experience.html",
        {
            "experience_form": form,
        },
    )


# Education Views
@login_required
def delete_education_view(request, pk):
    education = get_object_or_404(
        Education,
        pk=pk,
        profile=request.user.profile,
    )

    if request.method == "POST":

        Activity.objects.create(
            user=request.user,
            action=Activity.Action.DELETED,
            target=education,
        )

        education.delete()

        messages.success(request, "Education deleted successfully.")

        return redirect("accounts:edit_profile")

    return HttpResponseNotAllowed(["POST"])


@login_required
def edit_education_view(request, pk):
    education = get_object_or_404(
        Education,
        pk=pk,
        profile=request.user.profile,
    )

    if request.method == "POST":
        form = EducationForm(request.POST, instance=education)

        if form.is_valid():
            form.save()

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.UPDATED,
                target=education,
            )

            messages.success(request, "Education updated successfully.")

            return redirect("accounts:edit_profile")

    else:
        form = EducationForm(instance=education)

    return render(
        request,
        "portfolio/education/edit_education.html",
        {
            "education_form": form,
            "education": education,
        },
    )


@login_required
def add_education_view(request):
    if request.method == "POST":
        form = EducationForm(request.POST)

        if form.is_valid():
            education = form.save(commit=False)
            education.profile = request.user.profile
            education.save()

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.CREATED,
                target=education,
            )

            messages.success(request, "Education added successfully.")

            return redirect("accounts:edit_profile")

    else:
        form = EducationForm()

    return render(
        request,
        "portfolio/education/add_education.html",
        {
            "education_form": form,
        },
    )


# Project views
def projects_view(request):
    # One-Time Flag (clears bot filters on manual page refresh)
    is_fresh_bot_redirect = request.session.pop("bot_filters_fresh", False)
    is_pagination = "page" in request.GET

    if not is_fresh_bot_redirect and not is_pagination:
        if "bot_filters" in request.session:
            del request.session["bot_filters"]
            request.session.modified = True

    query = request.GET.get("q", "").strip()
    manual_status = request.GET.get("status", "").strip()

    bot_filters = request.session.get("bot_filters", {})

    bot_keywords_list = bot_filters.get("q", [])
    skills_list = bot_filters.get("skills", [])
    bot_status = bot_filters.get("status")

    # Query
    projects = Project.objects.select_related("profile__user").prefetch_related(
        "images", "skills"
    )

    # Title & Slug search
    if query:
        projects = projects.filter(Q(title__icontains=query) | Q(slug__icontains=query))

    elif bot_keywords_list and len(bot_keywords_list) > 0:
        search_conditions = Q()
        for phrase in bot_keywords_list:
            if phrase:
                clean_phrase = phrase.strip()
                search_conditions |= Q(title__icontains=clean_phrase)
                search_conditions |= Q(slug__icontains=clean_phrase)
                search_conditions |= Q(description__icontains=clean_phrase)

        projects = projects.filter(search_conditions)

    # Skills Filter
    if skills_list and len(skills_list) > 0:
        skill_conditions = Q()
        for skill in skills_list:
            if skill:
                skill_conditions |= Q(skills__name__icontains=skill)
        projects = projects.filter(skill_conditions)

    # Status Filter
    # Check if manual status is selected from UI
    if manual_status:
        projects = projects.filter(status=manual_status)
    # If no manual status, check if bot provided an array of statuses
    elif isinstance(bot_status, list) and len(bot_status) > 0:
        status_conditions = Q()
        for stat in bot_status:
            if stat:
                # Add each status to the OR condition
                status_conditions |= Q(status=stat)

        projects = projects.filter(status_conditions)

    # Distinct & Pagination
    projects = projects.distinct()

    paginator = Paginator(projects, 9)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "portfolio/project/Projects.html",
        {
            "page_obj": page_obj,
            "query": query,
            "has_bot_filters": bool(bot_filters and any(bot_filters.values())),
        },
    )


def project_details(request, slug):

    project = get_object_or_404(
        Project.objects.select_related("profile__user").prefetch_related(
            "images", "skills"
        ),
        slug=slug,
    )

    return render(
        request,
        "portfolio/project/project_details.html",
        {
            "project": project,
        },
    )


@login_required
def my_projects_view(request):
    if not hasattr(request.user, "profile"):
        messages.warning(
            request,
            "Create your profile first before view your projects.",
        )
        return redirect("accounts:create_profile")

    projects = (
        Project.objects.filter(profile=request.user.profile)
        .select_related("profile__user")
        .prefetch_related("images", "skills")
    )

    paginator = Paginator(projects, 9)

    page_number = request.GET.get("page", 1)

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "portfolio/project/my_projects.html",
        {
            "projects": page_obj,
        },
    )


@login_required
def add_project_view(request):
    if not hasattr(request.user, "profile"):
        messages.warning(
            request,
            "Create your profile first before adding projects.",
        )
        return redirect("accounts:create_profile")

    skills = Skill.objects.all()

    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.profile = request.user.profile

            project.save()

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.CREATED,
                target=project,
            )

            selected_skill_ids = request.POST.getlist("skills")
            project.skills.set(selected_skill_ids)

            # Project Images
            images = request.FILES.getlist("project_images")

            for index, image in enumerate(images, start=1):
                ProjectImage.objects.create(
                    project=project,
                    image=image,
                    display_order=index,
                )

            messages.success(request, "Project added successfully.")

            return redirect("portfolio:my_projects")

    else:
        form = ProjectForm()

    return render(
        request,
        "portfolio/project/add_project.html",
        {
            "project_form": form,
            "skills": skills,
        },
    )


@login_required
def edit_project_view(request, slug):
    if not hasattr(request.user, "profile"):
        messages.warning(
            request,
            "Create your profile first before editing projects.",
        )
        return redirect("accounts:create_profile")

    project = get_object_or_404(
        Project,
        slug=slug,
        profile=request.user.profile,
    )

    skills = Skill.objects.all()
    selected_skills = project.skills.all()

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            project = form.save()

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.UPDATED,
                target=project,
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

            project.skills.set(selected_skill_ids)

            # Project Images
            images = request.FILES.getlist("project_images")

            for index, image in enumerate(images, start=1):
                ProjectImage.objects.create(
                    project=project,
                    image=image,
                    display_order=index,
                )

            messages.success(request, "Project added successfully.")

            return redirect("portfolio:my_projects")

    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "portfolio/project/edit_project.html",
        {
            "project_form": form,
            "skills": skills,
            "selected_skills": selected_skills,
            "project": project,
        },
    )


@login_required
def delete_project_view(request, slug):
    project = get_object_or_404(
        Project,
        slug=slug,
        profile=request.user.profile,
    )

    if request.method == "POST":

        Activity.objects.create(
            user=request.user,
            action=Activity.Action.DELETED,
            target=project,
        )

        project.delete()

        messages.success(request, "Project deleted successfully.")

        return redirect("portfolio:my_projects")

    return HttpResponseNotAllowed(["POST"])


# project images views
@login_required
def manage_project_images_view(request, slug):
    if not hasattr(request.user, "profile"):
        messages.warning(
            request,
            "Create your profile first before managing project images.",
        )
        return redirect("accounts:create_profile")

    project = get_object_or_404(
        Project,
        slug=slug,
        profile=request.user.profile,
    )

    images = project.images.all()  # type: ignore

    if request.method == "POST":
        uploaded_images = request.FILES.getlist("project_images")

        for uploaded_image in uploaded_images:
            ProjectImage.objects.create(
                project=project,
                image=uploaded_image,
            )

        if uploaded_images:
            messages.success(
                request,
                "Images added successfully.",
            )

        return redirect(
            "portfolio:manage_project_images",
            slug=project.slug,
        )

    return render(
        request,
        "portfolio/projectimages/manage_project_images.html",
        {
            "project": project,
            "images": images,
        },
    )


@login_required
def delete_project_image_view(request, pk):
    image = get_object_or_404(
        ProjectImage,
        pk=pk,
        project__profile=request.user.profile,
    )

    if request.method == "POST":
        project = image.project

        image.delete()

        messages.success(request, "Image deleted successfully.")

        return redirect(
            "portfolio:manage_project_images",
            slug=project.slug,
        )

    return HttpResponseNotAllowed(["POST"])


@login_required
def edit_project_image_caption_view(request, pk):
    image = get_object_or_404(
        ProjectImage,
        pk=pk,
        project__profile=request.user.profile,
    )

    if request.method == "POST":
        caption = request.POST.get("caption", "").strip()

        image.caption = caption
        image.save(update_fields=["caption"])

        messages.success(
            request,
            "Caption updated successfully.",
        )

        return redirect(
            "portfolio:manage_project_images",
            slug=image.project.slug,
        )

    return HttpResponseNotAllowed(["POST"])
