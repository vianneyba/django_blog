from django.contrib import admin
from music import models

class BandAdmin(admin.ModelAdmin):
    search_fields = ['name']

class AlbumAdmin(admin.ModelAdmin):
    search_fields = ['band__name']
    list_display = ['band', 'title', 'release_year']

admin.site.register(models.Track)
admin.site.register(models.Band, BandAdmin)
admin.site.register(models.Album, AlbumAdmin)
admin.site.register(models.Listening_History)
admin.site.register(models.Links_Review)
