from django.contrib import admin
from magazine import models


class ArticleAdminMag(admin.ModelAdmin):
    readonly_fields = ["slug"]
    exclude = []

admin.site.register(models.Article, ArticleAdminMag)
admin.site.register(models.Page)
admin.site.register(models.Magazine)