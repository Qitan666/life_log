from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    list_editable = ('is_published',)
    raw_id_fields = ('author',)
    actions = ['unpublish_posts', 'publish_posts']

    @admin.action(description='Unpublish selected posts')
    def unpublish_posts(self, request, queryset):
        n = queryset.update(is_published=False)
        self.message_user(request, f'Unpublished {n} post(s).')

    @admin.action(description='Publish selected posts')
    def publish_posts(self, request, queryset):
        n = queryset.update(is_published=True)
        self.message_user(request, f'Published {n} post(s).')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)
    raw_id_fields = ('post', 'author')

    def content_short(self, obj):
        return obj.content[:50] + '…' if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Content'
