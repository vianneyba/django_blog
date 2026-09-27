from django import forms
from django.contrib import admin
from dal import autocomplete

from music import models

class TrackForm(forms.ModelForm):
    album = forms.ModelChoiceField(
        queryset=models.Album.objects.all(),
        widget=autocomplete.ModelSelect2(url="music:album-autocomplete"),
    )

    class Meta:
        model = models.Track
        fields = "__all__"

class AlbumForm(forms.ModelForm):
    band = forms.ModelChoiceField(
        queryset=models.Band.objects.all(),
        widget=autocomplete.ModelSelect2(url="music:band-autocomplete"),
    )

    class Meta:
        model = models.Album
        fields = "__all__"

@admin.register(models.Track)
class TrackAdmin(admin.ModelAdmin):
    form = TrackForm

@admin.register(models.Band)
class BandAdmin(admin.ModelAdmin):
    search_fields = ["name"]

@admin.register(models.Album)
class AlbumAdmin(admin.ModelAdmin):
    form = AlbumForm
    search_fields = ["band__name", "title"]
    list_display = ["band", "title", "release_year"]

admin.site.register(models.Listening_History)
admin.site.register(models.Links_Review)