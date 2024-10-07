from django.contrib import admin
from polls import models

# class Liste_TitleAdmin(admin.ModelAdmin):
#     exclude = ["slug"]


admin.site.register(models.Title_Suggestion)
admin.site.register(models.Liste_Title)
admin.site.register(models.Choice_Liste_Title)
