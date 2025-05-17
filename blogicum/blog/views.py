from django.http import Http404

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PostForm, CommentForm, ProfileEditForm
from .models import Post, Comment, User, Category


def get_published_posts():
    return (
        Post.objects
        .select_related('category', 'author')
        .filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
        .order_by('-pub_date')
    )


def index(request):
    posts = Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    post = get_object_or_404(Post, id=id)

    if not post.is_published and request.user != post.author:
        raise Http404("Пост не найден.")

    if (post.category
        and not post.category.is_published
            and request.user != post.author):
        raise Http404("Пост не найден.")

    if post.pub_date > timezone.now() and request.user != post.author:
        raise Http404("Пост не найден.")

    comments = post.comments.select_related('author').all()

    form = CommentForm()
    if request.user.is_authenticated:
        pass
    else:
        form = None

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'user': request.user,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = category.posts.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
        'post_list': page_obj.object_list,
        'paginator': paginator,
    }
    return render(request, 'blog/category.html', context)


def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    form = ProfileEditForm(
        instance=profile_user) if request.user == profile_user else None

    posts_queryset = profile_user.posts.all()

    if request.user != profile_user:
        posts_queryset = posts_queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    posts = posts_queryset.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile_user,
        'page_obj': page_obj,
        'paginator': paginator,
        'user': request.user,
        'form': form,
        'edit_mode': False
    }
    return render(request, 'blog/profile.html', context)


@login_required
def user_profile_edit(request):
    user = request.user

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=user.username)
    else:
        form = ProfileEditForm(instance=user)

    return render(request, 'blog/user.html', {
        'form': form,
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()

    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user != post.author:
        return redirect('blog:post_detail', id=id)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=id)
    else:
        form = PostForm(instance=post)

    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, id):
    """Добавляет комментарий к посту."""
    post = get_object_or_404(Post, id=id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('blog:post_detail', id=id)
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
        'post_id': post_id,
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
    """Удаляет комментарий."""
    comment = get_object_or_404(Comment, id=comment_id, post__id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)
    context = {
        'comment': comment,
        'post_id': post_id,
    }
    return render(request, 'blog/comment.html', context)
