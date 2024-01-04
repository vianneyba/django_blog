from django.contrib import admin
from magazine import models

admin.site.register(models.Article)
admin.site.register(models.Insert)
admin.site.register(models.PhotoInsert)
admin.site.register(models.Opinion)
admin.site.register(models.Score)
admin.site.register(models.PhotoArticle)
admin.site.register(models.Link)
admin.site.register(models.Paragraph)
