from django.contrib import admin
from magazine import models


class ArticleAdmin(admin.ModelAdmin):
    readonly_fields = ["slug"]
    exclude = []

admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.Page)
admin.site.register(models.Magazine)