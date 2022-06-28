from django.contrib import admin
from music import models

admin.site.register(models.Track)
admin.site.register(models.Band)
admin.site.register(models.Album)
