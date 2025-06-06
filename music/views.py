from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from music import models, serializers
from datetime import datetime
from django.contrib import messages
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.viewsets import ViewSet

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
            elif request.GET.get('code'):
                code = request.GET.get('code')
                album = models.Album.objects.get(code=code)
                return render(request, 'music/view_album.html', {'album': album})

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
            q = request.GET.get('search').strip()
            albums = albums.filter(Q(band__name__icontains=q) | Q(title__icontains=q))
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

def add_link(request, pk):
    album = models.Album.objects.get(pk=pk)
    link_str = request.POST.get('link')
    name_link = request.POST.get('name')

    models.Links_Review.objects.create(album=album, link=link_str, name=name_link)

    return redirect('music:view-album', pk=pk)

def add_history(request):
    result = ""
    if request.method == 'POST':
        text = request.POST.get('history')
        lines = text.split('\n')
        for line in lines:
            info = line.strip().split(';')
            if len(info) == 4:
                title_album = info[0]
                title_track = info[1]
                band = info[2]
                listening_date = info[3]

                album = models.Album.objects.filter(title__iexact=title_album, band__name__iexact=band)
                print(f"=====> {album}")
                if len(album) == 1:
                    track = album[0].tracks.filter(title__iexact=title_track)
                    print(f"=====> {track}")
                    if len(track) == 1:
                        listening_date = datetime.strptime(info[3], "%d %b %Y, %I:%M%p")
                        entry = models.Listening_History.objects.filter(listening_date=listening_date)
                        print(f"=====> {entry}")
                        if len(entry) == 0:
                            models.Listening_History.objects.create(track=track[0], listening_date=listening_date)
                            messages.success(request, f"{band} - {title_album} - {title_track} - {listening_date}")
                        else:
                            messages.info(request, f"{line} existe deja")
                    else:
                        result = result + line + "\n"
                        messages.error(request, f"{title_track} n'existe pas")
                else:
                    result = result + line + "\n"
                    messages.error(request, f"{band} ou {title_album} n'existe pas")
            else:
                result = result + line + "\n"
                messages.error(request, f"Mauvais formatage de la ligne: {line}")

    return render(request, 'music/form_history.html', {'result': result})

def view_history(request):
    year = request.GET.get('year')
    month = request.GET.get('month')

    queryset = models.Listening_History.objects.all().order_by('-listening_date')

    if year:
        queryset = queryset.filter(listening_date__year=year)
    if month:
        queryset = queryset.filter(listening_date__month=month)

    paginator = Paginator(queryset, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'music/view_history.html', {
        'page_obj': page_obj,
        'year': year,
        'month': month
    })

@staff_member_required
def view_album_by_code(request, pk):
    album = models.Album.objects.get(code=pk)

    return render(request, 'music/view_album.html', {'album': album})

class AlbumList(viewsets.ModelViewSet):

    queryset= models.Album.objects.all()
    serializer_class= serializers.AlbumSerializer
    permission_classes= (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = models.Album.objects.all().order_by('band__name')
        if self.request.query_params.get('band') is not None:
            pk = self.request.query_params.get('band')
            queryset = queryset.filter(band_id=pk)
        if self.request.query_params.get('search') is not None:
            word = self.request.query_params.get('search')
            queryset = queryset.filter(Q(band__name__icontains=word) | Q(title__icontains=word))
        if self.request.query_params.get('year') is not None:
            year = self.request.query_params.get('year')
            queryset = queryset.filter(release_year=year)
        if self.request.query_params.get('score') is not None:
            score = self.request.query_params.get('score')
            queryset = queryset.filter(score__gte=score)
        if self.request.query_params.get('top_track') is not None:
            score = self.request.query_params.get('top_track')
            queryset = queryset.filter(tracks__score=score).distinct()
        if self.request.query_params.get('code') is not None:
            code = self.request.query_params.get('code')
            queryset = queryset.filter(code=code).distinct()
        return queryset
    
class AlbumTrack(viewsets.ModelViewSet):
    queryset= models.Track.objects.all()
    serializer_class= serializers.AddTrackSerializer
    permission_classes= (permissions.IsAuthenticatedOrReadOnly,)
    def get_queryset(self):
        queryset = models.Track.objects.all()
        return queryset
    
class TrackListeningView(ViewSet):  # <– Hérite de ViewSet
    permission_classes= (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request):
        serializer = serializers.ListeningHistorySerializer(data=request.data)
        if serializer.is_valid():
            listening = serializer.save()
            return Response({"status": "success", "listening_id": listening.id})
        return Response(serializer.errors, status=400)
