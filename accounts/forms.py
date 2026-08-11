from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile

User = get_user_model()


class RegisterForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
        )

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class LoginForm(AuthenticationForm):

    username = forms.CharField(label="Username or Email")

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super(forms.Form, self).clean()

        username_or_email = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if not username_or_email or not password:
            return cleaned_data

        user = User.objects.filter(email__iexact=username_or_email).first()

        username = user.username if user else username_or_email

        self.user_cache = authenticate(
            self.request,
            username=username,
            password=password,
        )

        if self.user_cache is None:
            raise forms.ValidationError("Invalid username/email or password.")

        self.confirm_login_allowed(self.user_cache)

        return cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "username",
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "avatar",
            "jop_title",
            "bio",
            "about",
            "resume",
            "github_url",
            "linkedin_url",
            "website_url",
            "location",
            "available_for_work",
        )
