from django.contrib import admin
from .models import LikeArticle

class LikeAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'is_like')

admin.site.register(LikeArticle, LikeAdmin)