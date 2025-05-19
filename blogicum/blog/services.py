from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from .constants import POST_ORDERING, POSTS_PER_PAGE
from .models import Post


def get_posts_queryset(
    queryset=None,
    for_admin_or_author=False,
    add_comment_count=True,
):
    if queryset is None:
        queryset = Post.objects.all()

    queryset = queryset.select_related('category', 'author', 'location')

    if not for_admin_or_author:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )

    if add_comment_count:
        queryset = queryset.annotate(comment_count=Count('comments'))

    queryset = queryset.order_by(POST_ORDERING)

    return queryset


def get_paginated_queryset(request, queryset, per_page=POSTS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
