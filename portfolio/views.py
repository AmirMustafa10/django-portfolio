from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from .models import Experience, Education, Project, Skill, ProjectImage
from .forms import EducationForm, ExperienceForm, ProjectForm
from django.contrib import messages
from django.db.models import Q


# Experience views
@login_required
def delete_experience_view(request, pk):
    experience = get_object_or_404(
        Experience,
        pk=pk,
        profile=request.user.profile,
    )

    if request.method == "POST":
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

            messages.success(request, "Experience updated successfully.")

            return redirect("accounts:edit_profile")

    else:
        form = ExperienceForm(instance=experience)

    return render(
        request,
        "portfolio/edit_experience.html",
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

            messages.success(request, "Experience added successfully.")

            return redirect("accounts:edit_profile")

    else:
        form = ExperienceForm()

    return render(
        request,
        "portfolio/add_experience.html",
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

            messages.success(request, "Education updated successfully.")

            return redirect("accounts:edit_profile")

    else:
        form = EducationForm(instance=education)

    return render(
        request,
        "portfolio/edit_education.html",
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

            messages.success(request, "Education added successfully.")

            return redirect("accounts:edit_profile")

    else:
        form = EducationForm()

    return render(
        request,
        "portfolio/add_education.html",
        {
            "education_form": form,
        },
    )


# Project views
def projects_view(request):

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    projects = Project.objects.select_related("profile__user").prefetch_related(
        "images", "skills"
    )

    if query:
        projects = projects.filter(Q(title__icontains=query) | Q(slug__icontains=query))

    if status:
        projects = projects.filter(status=status)

    projects = projects.distinct()

    return render(
        request,
        "portfolio/Projects.html",
        {
            "Projects": projects,
            "query": query,
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
        "portfolio/project_details.html",
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

    return render(
        request,
        "portfolio/my_projects.html",
        {
            "projects": projects,
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
        "portfolio/add_project.html",
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
        "portfolio/edit_project.html",
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
        project.delete()

        messages.success(request, "Project deleted successfully.")

        return redirect("portfolio:my_projects")

    return HttpResponseNotAllowed(["POST"])