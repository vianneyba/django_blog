from django.contrib import admin
from blog.models import Article, Category, Tag

@admin.action(description="Mark selected stories as published")
def make_published(ArticleAdmin, request, queryset):
    queryset.update(published=True)


class BlogAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title', 'author', 'published')
    list_filter = ('published',)
    prepopulated_fields = {"slug": ("title",)}
    actions = [make_published]


admin.site.register(Article, BlogAdmin)
admin.site.register(Category)
admin.site.register(Tag)