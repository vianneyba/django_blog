from django.contrib import admin
from .models import LikeArticle, LikeComment

class LikeArticleAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'is_like')

class LikeCommentAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'is_like')

admin.site.register(LikeArticle, LikeArticleAdmin)
admin.site.register(LikeComment, LikeCommentAdmin)