from django import forms
from .models import Skill, Experience, Education, Project


class SkillForm(forms.ModelForm):

    class Meta:
        model = Skill
        fields = (
            "name",
            "icon",
        )


class ExperienceForm(forms.ModelForm):

    class Meta:
        model = Experience
        fields = (
            "company_name",
            "job_title",
            "employment_type",
            "description",
            "start_date",
            "end_date",
            "currently_working",
        )


class EducationForm(forms.ModelForm):

    class Meta:
        model = Education
        fields = (
            "institution",
            "degree",
            "field_of_study",
            "start_date",
            "end_date",
            "grade",
            "description",
        )


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = (
            "title",
            "description",
            "status",
            "live_demo_url",
            "source_code_url",
            "is_featured",
        )
