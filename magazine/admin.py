from django.contrib import admin
from magazine import models

class ArticleAdmin(admin.ModelAdmin):
    exclude = []

class ParagraphAdmin(admin.ModelAdmin):
    exclude = ["id_num"]

class OpinionAdmin(admin.ModelAdmin):
    exclude = ["id_num"]

class PhotoArticleAdmin(admin.ModelAdmin):
    exclude = ["id_num", "link"]

class InsertAdmin(admin.ModelAdmin):
    exclude = ["id_num"]

class PhotoInsertAdmin(admin.ModelAdmin):
    exclude = ["id_num", "link"]

admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.Insert, InsertAdmin)
admin.site.register(models.PhotoInsert, PhotoInsertAdmin)
admin.site.register(models.Opinion, OpinionAdmin)
admin.site.register(models.Score)
admin.site.register(models.PhotoArticle, PhotoArticleAdmin)
admin.site.register(models.Link)
admin.site.register(models.Paragraph, ParagraphAdmin)
