from django.contrib import admin
from blog.models import Article, Category, Tag

class BlogAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title', 'author', 'published')
    list_filter = ('published',)
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Article, BlogAdmin)
admin.site.register(Category)
admin.site.register(Tag)