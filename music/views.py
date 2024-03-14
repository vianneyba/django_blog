from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from music import models, serializers

def return_paginator(request, queryset):
    paginator = Paginator(queryset, 33*3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj

@staff_member_required
def index(request):

    if 'type' in request.GET:
        if request.GET.get('type') == 'tracks':
            track_score = request.GET.get('note')
            tracks = models.Track.objects.filter(score__gte=track_score).order_by('-score')
            context = {'page_obj': return_paginator(request, tracks), 'my_type': 'tracks', 'note': track_score}
        elif request.GET.get('type') == 'albums':
            albums = models.Album.objects.all().order_by('-pk')
            if request.GET.get('note'):
                note = request.GET.get('note')
                albums = albums.filter(score__gte=note).order_by('-score')
                context = {'page_obj': return_paginator(request, albums), 'my_type': 'albums'}

            context = {'page_obj': return_paginator(request, albums), 'my_type': 'albums'}
        else:
                albums = models.Album.objects.all().order_by('-pk')
                context = {'page_obj': return_paginator(request, albums), 'my_type': 'albums'}
        
    else:
        albums = models.Album.objects.all().order_by('-pk')
        context = {'page_obj': return_paginator(request, albums), 'my_type': 'albums'}
        if request.GET.get('date'):
            release_year = request.GET.get('date')
            albums = albums.filter(release_year=release_year)
        if request.GET.get('band'):
            band = request.GET.get('band')
            albums = albums.filter(band=band)
        if request.GET.get('search'):
            q = request.GET.get('search')
            albums = albums.filter(Q(band__name__icontains=q) | Q(title__icontains=q))
        if request.GET.get('code'):
            code = request.GET.get('code')
            albums = albums.get(code=code)
        context = {'page_obj': return_paginator(request, albums), 'my_type': 'albums'}
    return render(request, 'music/index.html', context)

@staff_member_required
def view_album(request, pk):
    album = models.Album.objects.get(pk=pk)

    return render(request, 'music/view_album.html', {'album': album})

@staff_member_required
def music_add_track_note(request):
    album_id = request.GET.get('album')
    track_id = request.GET.get('track')
    note = int(request.GET.get('note'))

    track = models.Track.objects.get(pk=track_id)
    if note > 0 and note < 6:
        track.score = note
        track.save()

    return redirect('music:view-album', pk=album_id)

@staff_member_required
def music_add_album_note(request):
    album_id = request.GET.get('album')
    note = int(request.GET.get('note'))

    album = models.Album.objects.get(pk=album_id)
    if note > 0 and note < 6:
        album.score = note
        album.save()

    return redirect('music:view-album', pk=album_id)

@staff_member_required
def view_album_by_code(request, pk):
    album = models.Album.objects.get(code=pk)

    return render(request, 'music/view_album.html', {'album': album})

class AlbumList(viewsets.ModelViewSet):

    queryset= models.Album.objects.all()
    serializer_class= serializers.AlbumSerializer
    permission_classes= (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = models.Album.objects.all()
        if self.request.query_params.get('band') is not None:
            print('by id band')
            pk = self.request.query_params.get('band')
            queryset = queryset.filter(band_id=pk)

        return queryset