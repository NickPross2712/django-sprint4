from django.contrib import admin

from .constants import COMMENT_ADMIN_TEXT_SHORT_LENGTH
from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')
    list_filter = ('is_published',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published')
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'category', 'is_published')
    search_fields = ('title', 'text', 'author__username', 'category__title')
    list_filter = ('is_published', 'category', 'author', 'pub_date')
    date_hierarchy = 'pub_date'
    ordering = ('-pub_date',)
    raw_id_fields = ('author', 'category', 'location')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_date', 'text_short')
    search_fields = ('text', 'author__username', 'post__title')
    list_filter = ('post', 'author', 'created_date')
    date_hierarchy = 'created_date'
    ordering = ('-created_date',)
    raw_id_fields = ('post', 'author')

    @admin.display(description=('Текст комментария'))
    def text_short(self, obj):
        if len(obj.text) > COMMENT_ADMIN_TEXT_SHORT_LENGTH:
            return obj.text[:COMMENT_ADMIN_TEXT_SHORT_LENGTH] + '...'
        else:
            return obj.text
