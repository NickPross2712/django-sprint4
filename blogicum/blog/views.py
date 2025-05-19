from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, ProfileEditForm
from .models import Category, Comment, Post
from .services import get_paginated_queryset, get_posts_queryset

User = get_user_model()


def index(request):
    posts = get_posts_queryset()

    page_obj = get_paginated_queryset(request, posts)

    context = {
        'page_obj': page_obj,
        'paginator': page_obj.paginator,
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    queryset = get_posts_queryset(
        for_admin_or_author=True,
        add_comment_count=True,
    )

    post = get_object_or_404(
        queryset.filter(
            Q(author=request.user) | Q(pub_date__lte=timezone.now()),
            Q(author=request.user) | Q(is_published=True),
            (
                Q(author=request.user)
                | Q(category__is_published=True)
                | Q(category__isnull=True)
            ),
        ),
        id=id,
    )

    comments = post.comments.select_related('author').all()
    form = None
    if request.user.is_authenticated:
        form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    initial_category_posts = category.posts.all()

    posts_queryset = get_posts_queryset(
        queryset=initial_category_posts,
        add_comment_count=True,
    )

    page_obj = get_paginated_queryset(request, posts_queryset)

    context = {
        'category': category,
        'page_obj': page_obj,
        'paginator': page_obj.paginator,
    }
    return render(request, 'blog/category.html', context)


def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    form = None
    edit_mode = False
    posts_queryset = profile_user.posts.all()

    if request.user == profile_user:
        form = ProfileEditForm(instance=profile_user)
        edit_mode = True

    posts = get_posts_queryset(
        queryset=posts_queryset,
        for_admin_or_author=request.user == profile_user,
    )

    page_obj = get_paginated_queryset(request, posts)

    context = {
        'profile': profile_user,
        'page_obj': page_obj,
        'form': form,
        'edit_mode': edit_mode,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def user_profile_edit(request):
    user = request.user

    form = ProfileEditForm(request.POST or None, instance=user)

    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=user.username)

    return render(request, 'blog/user.html', {
        'form': form,
    })


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user != post.author:
        return redirect('blog:post_detail', id=id)

    form = PostForm(request.POST or None, request.FILES or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=id)

    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)

    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

    return redirect('blog:post_detail', id=id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment, id=comment_id, post__id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=post_id)

    context = {
        'form': form,
        'comment': comment,
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user != post.author:
        return redirect('blog:post_detail', id=id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')

    context = {
        'post': post,
    }
    return render(request, 'blog/post_delete_confirm.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)
    context = {
        'comment': comment,
    }
    return render(request, 'blog/comment.html', context)
