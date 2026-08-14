from django import forms
from .models import BlogPost, Comment


class BlogForm(forms.ModelForm):

    class Meta:
        model = BlogPost
        fields = (
            "title",
            "content",
            "cover_image",
            "status",
        )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = (
            "content",
        )
