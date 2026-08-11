from django import forms
from .models import Skill, Experience, Education


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
