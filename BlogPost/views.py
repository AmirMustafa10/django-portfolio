from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import BlogPost, Comment
from .form import BlogForm, CommentForm
from core.models import Activity


# Blog views
def blogpost_view(request):
    is_fresh_bot_redirect = request.session.pop("bot_filters_fresh", False)
    is_pagination = "page" in request.GET

    # Clear filters if it's a normal refresh/visit
    if not is_fresh_bot_redirect and not is_pagination:
        if "bot_filters" in request.session:
            del request.session["bot_filters"]
            request.session.modified = True

    query = request.GET.get("q", "").strip()

    bot_filters = request.session.get("bot_filters", {})
    bot_keywords_list = bot_filters.get("q", [])

    blogs = (
        BlogPost.objects.select_related("profile__user")
        .annotate(comment_count=Count("comments"))
        .order_by("-created_at")
    )

    if query:
        blogs = blogs.filter(
            Q(title__icontains=query)
            | Q(slug__icontains=query)
            | Q(content__icontains=query)
        )
    elif bot_keywords_list and len(bot_keywords_list) > 0:
        search_conditions = Q()
        for phrase in bot_keywords_list:
            if phrase:
                clean_phrase = phrase.strip()
                search_conditions |= Q(title__icontains=clean_phrase)
                search_conditions |= Q(content__icontains=clean_phrase)
                search_conditions |= Q(slug__icontains=clean_phrase)

        blogs = blogs.filter(search_conditions)

    blogs = blogs.filter(status=BlogPost.Status.PUBLISHED)

    paginator = Paginator(blogs, 9)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/blogs.html",
        {
            "page_obj": page_obj,
            "query": query,
            "has_bot_filters": bool(bot_filters and any(bot_filters.values())),
        },
    )


def blogpost_details_view(request, slug):
    blog = get_object_or_404(
        BlogPost,
        slug=slug,
    )

    if blog.status == BlogPost.Status.DRAFT and blog.profile.user != request.user:
        raise Http404

    comments = (
        blog.comments.filter(parent__isnull=True)  # type: ignore
        .select_related("user__profile")
        .prefetch_related("replies__user")
        .order_by("-created_at")
    )

    comments_count = comments.count()

    paginator = Paginator(comments, 10)

    page_number = request.GET.get("page", 1)

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/blog_details.html",
        {
            "blog": blog,
            "comments": page_obj,
            "comments_count": comments_count,
        },
    )


# Comment views
@login_required
def add_comment_view(request, blog_slug):
    blog = get_object_or_404(
        BlogPost,
        slug=blog_slug,
        status=BlogPost.Status.PUBLISHED,
    )

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            parent = None
            parent_id = request.POST.get("parent_id")

            if parent_id:
                parent = get_object_or_404(
                    Comment,
                    pk=parent_id,
                )

                if parent.blog_post != blog:
                    messages.error(request, "Invalid parent comment.")
                    return redirect(
                        "blog:blog_details",
                        slug=blog_slug,
                    )

            comment = form.save(commit=False)
            comment.user = request.user
            comment.blog_post = blog
            comment.parent = parent
            comment.save()

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.CREATED,
                target=comment,
            )

            messages.success(
                request,
                (
                    "Reply added successfully."
                    if parent
                    else "Comment added successfully."
                ),
            )

            return redirect(
                "blog:blog_details",
                slug=blog_slug,
            )

    else:
        form = CommentForm()

    return render(
        request,
        "blog/blog_details.html",
        {
            "blog": blog,
            "comment_form": form,
        },
    )


@login_required
def edit_comment_view(request, blog_slug, comment_id):
    blog = get_object_or_404(
        BlogPost,
        slug=blog_slug,
        status=BlogPost.Status.PUBLISHED,
    )

    comment = get_object_or_404(
        Comment,
        id=comment_id,
        blog_post=blog,
        user=request.user,
    )

    if request.method == "POST":
        form = CommentForm(
            request.POST,
            instance=comment,
        )

        if form.is_valid():
            form.save()

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.UPDATED,
                target=comment,
            )

            messages.success(
                request,
                "Comment edited successfully.",
            )

            return redirect(
                "blog:blog_details",
                slug=blog_slug,
            )

    return redirect(
        "blog:blog_details",
        slug=blog_slug,
    )


@login_required
def delete_comment_view(request, pk):
    comment = get_object_or_404(
        Comment,
        id=pk,
        user=request.user,
    )

    if request.method == "POST":

        Activity.objects.create(
            user=request.user,
            action=Activity.Action.DELETED,
            target=comment,
        )

        comment.delete()

        messages.success(request, "Comment deleted successfully.")

        return redirect("blog:blog_details", slug=comment.blog_post.slug)

    return HttpResponseNotAllowed(["POST"])


# My Blogs views
@login_required
def my_blogs_view(request):
    if not hasattr(request.user, "profile"):
        messages.warning(
            request,
            "Create your profile first before view your blogs.",
        )
        return redirect("accounts:create_profile")

    status = request.GET.get("status", "").strip()

    blogs = (
        BlogPost.objects.filter(profile=request.user.profile)
        .select_related("profile__user")
        .annotate(comment_count=Count("comments"))
        .order_by("-created_at")
    )

    if status in {
        BlogPost.Status.DRAFT,
        BlogPost.Status.PUBLISHED,
    }:
        blogs = blogs.filter(status=status)

    paginator = Paginator(blogs, 9)

    page_number = request.GET.get("page", 1)

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/myblogs.html",
        {
            "page_obj": page_obj,
            "status": status,
        },
    )


@login_required
def add_blog_view(request):
    profile = request.user.profile

    if request.method == "POST":
        form = BlogForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            blog = form.save(commit=False)
            blog.profile = profile
            blog.save()

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.CREATED,
                target=blog,
            )

            messages.success(
                request,
                "Blog added successfully.",
            )

            return redirect("blog:my_blogs")

    else:
        form = BlogForm()

    return render(
        request,
        "blog/add_blog.html",
        {
            "blog_form": form,
        },
    )


@login_required
def edit_blog_view(request, blog_slug):
    blog = get_object_or_404(BlogPost, slug=blog_slug, profile=request.user.profile)

    if request.method == "POST":
        form = BlogForm(
            request.POST,
            request.FILES,
            instance=blog,
        )

        if form.is_valid():
            form.save()

            Activity.objects.create(
                user=request.user,
                action=Activity.Action.UPDATED,
                target=blog,
            )

            messages.success(
                request,
                "Blog edited successfully.",
            )

            return redirect("blog:my_blogs")

    else:
        form = BlogForm(
            instance=blog,
        )

    return render(
        request,
        "blog/edit_blog.html",
        {
            "blog_form": form,
            "blog": blog,
        },
    )


@login_required
def delete_blog_view(request, pk):
    blog = get_object_or_404(
        BlogPost,
        id=pk,
        profile=request.user.profile,
    )

    if request.method == "POST":

        Activity.objects.create(
            user=request.user,
            action=Activity.Action.DELETED,
            target=blog,
        )

        blog.delete()

        messages.success(request, "Blog deleted successfully.")

        return redirect("blog:my_blogs")

    return HttpResponseNotAllowed(["POST"])
