from django.contrib import admin

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
    # Предполагается наличие поля slug в модели Post
    prepopulated_fields = {'slug': ('title',)}
    # Улучшает отображение внешних ключей при большом количестве записей
    raw_id_fields = ('author', 'category', 'location')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_date',
                    'is_published', 'text_short')
    search_fields = ('text', 'author__username', 'post__title')
    list_filter = ('is_published', 'post', 'author', 'created_date')
    date_hierarchy = 'created_date'
    ordering = ('-created_date',)
    raw_id_fields = ('post', 'author')

    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_short.short_description = 'Текст комментария'
