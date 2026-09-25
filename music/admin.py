from django.contrib import admin
from music import models
from django import forms
from dal import autocomplete

class Album_TrackForm(forms.ModelForm):
    album = forms.ModelMultipleChoiceField(
        queryset=models.Album.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='music:album-autocomplete')
    )

    class Meta:
        model = models.Album
        fields = '__all__'

class Album_BandForm(forms.ModelForm):
    band = forms.ModelMultipleChoiceField(
        queryset=models.Band.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='music:band-autocomplete')
    )

    class Meta:
        model = models.Album
        fields = '__all__'

class TrackAdmin(admin.ModelAdmin):
    form = Album_TrackForm

class BandAdmin(admin.ModelAdmin):
    search_fields = ['name']

class AlbumAdmin(admin.ModelAdmin):
    search_fields = ['band__name']
    list_display = ['band', 'title', 'release_year']
    form = Album_BandForm

admin.site.register(models.Track, TrackAdmin)
admin.site.register(models.Band, BandAdmin)
admin.site.register(models.Album, AlbumAdmin)
admin.site.register(models.Listening_History)
admin.site.register(models.Links_Review)
