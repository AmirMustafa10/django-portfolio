from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from .models import Experience, Education, Project
from .forms import EducationForm, ExperienceForm
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



