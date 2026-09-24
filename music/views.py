from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from music import models, serializers
from datetime import datetime, date
from django.contrib import messages
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.viewsets import ViewSet
import os
import math

def return_paginator(request, queryset):
    paginator = Paginator(queryset, 33*3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj

@staff_member_required
def index(request):
    context = {}

    if 'type' in request.GET:
        print(f"==> type existe {request.GET['type']}")
        if request.GET.get('type') == 'tracks':
            track_score = request.GET.get('note')
            tracks = models.Track.objects.filter(score__gte=track_score).order_by('-score')
            context = {
                'page_obj': return_paginator(request, tracks),
                'my_type': 'tracks',
                'note': track_score,
                'url': "?type=tracks&note=4"}
        elif request.GET.get('type') == 'albums':
            albums = models.Album.objects.all().order_by('-pk')
            context = dict()
            context['url'] = "?type=albums"
            if request.GET.get('note'):
                note = request.GET.get('note')
                albums = albums.filter(score__gte=note).order_by('-score')
                context['url'] = "?type=albums&note=4"
            elif request.GET.get('code'):
                code = request.GET.get('code')
                album = models.Album.objects.get(code=code)
                return render(request, 'music/view_album.html', {'album': album, "view_menu": True})

            context['page_obj'] = return_paginator(request, albums)
            context['my_type'] = 'albums'
  
        else:
            albums = models.Album.objects.all().order_by('-pk')
            context = {
                'page_obj': return_paginator(request, albums),
                'my_type': 'albums',}
        
    else:
        albums = models.Album.objects.all().order_by('-pk')
        url = "?type=albums"
        if request.GET.get('date'):
            release_year = request.GET.get('date')
            albums = albums.filter(release_year=release_year)
            url = f"{url}&date={release_year}"
        if request.GET.get('band'):
            band = request.GET.get('band')
            albums = albums.filter(band=band)
            url = f"{url}&band={band}"
        if request.GET.get('search'):
            q = request.GET.get('search').strip()
            albums = albums.filter(Q(band__name__icontains=q) | Q(title__icontains=q))
            url = f"{url}&search={q}"
        context = {
            'page_obj': return_paginator(request, albums),
            'my_type': 'albums',
            'url': url}

    context['view_menu'] = True
    return render(request, 'music/index.html', context)

@staff_member_required
def view_album(request, pk):
    repertoire = os.path.join(settings.BASE_DIR, 'static/lyrics')
    album = models.Album.objects.get(pk=pk)

    tracks = []
    for track in album.tracks.all():
        try:
            with open(f'{repertoire}/{album.id}-{track.id}.txt', "r") as f:
                track.withlyrics = True
        except FileNotFoundError:
            pass

        tracks.append(track)

    return render(request, 'music/view_album.html', {
        'album': album,
        'tracks': tracks,
        'view_menu': True,
        'view_search_bar': True
        })

@staff_member_required
def music_add_track_note(request):
    album_id = request.GET.get('album')
    track_id = request.GET.get('track')
    note = int(request.GET.get('note'))

    track = models.Track.objects.get(pk=track_id)
    if note > 0 and note < 6:
        track.score = note
        track.save()

    if "url" in request.GET:
        return redirect(request.GET.get('url'))
    else:
        return redirect('music:view-album', pk=album_id)

@staff_member_required
def music_add_album_note(request):
    album_id = request.GET.get('album')
    note = int(request.GET.get('note'))

    album = models.Album.objects.get(pk=album_id)
    if note > 0 and note < 6:
        album.score = note
        album.save()

    if "url" in request.GET:
        return redirect(request.GET.get('url'))
    else:
        return redirect('music:view-album', pk=album_id)

@staff_member_required
def add_link(request, pk):
    album = models.Album.objects.get(pk=pk)
    link_str = request.POST.get('link')
    name_link = request.POST.get('name')

    models.Links_Review.objects.create(album=album, link=link_str, name=name_link)

    return redirect('music:view-album', pk=pk)

@staff_member_required
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
                if len(album) == 1:
                    track = album[0].tracks.filter(title__iexact=title_track)
                    if len(track) == 1:
                        listening_date = datetime.strptime(info[3], "%d %b %Y, %I:%M%p")
                        entry = models.Listening_History.objects.filter(listening_date=listening_date)
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

@staff_member_required
def view_history(request):

    queryset = models.Listening_History.objects.all().order_by('-listening_date')
    url = f"?"
    choice = {
        'year': "listening_date__year",
        'month': 'listening_date__month',
        'day': "listening_date__day",
        'band': 'track__album__band',
        'album': 'track__album',
        'title': 'track_id',
        'note': 'track__score__gte',
        'score': 'track__album__score__gte',
        'from': 'listening_date__gte'
        }

    nombre_jours = (date.today() - date(2006, 7, 6)).days
    for key, value in request.GET.items():
        if key in choice:
            if key == 'day':
               nombre_jours = 1
            elif key == 'month':
                nombre_jours = 31
            elif key == 'year':
                nombre_jours = 365
            elif key == 'from':
                date_cible_str = value
                date_cible = datetime.strptime(date_cible_str, "%Y-%m-%d").date()

                aujourdhui = date.today()

                difference = date_cible - aujourdhui
                nombre_jours = difference.days*-1

            if key == 'from':
                # my_date = value.split("-")
                filters = {choice[key]: date_cible}
                queryset = queryset.filter(**filters)
            else:
                filters = {choice[key]: value}
                queryset = queryset.filter(**filters)

            url = f"{url}{key}={value}&"

    paginator = Paginator(queryset, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    Scrobbles = len(queryset)

    return render(request, 'music/view_history.html', {
        'page_obj': page_obj,
        'url': url,
        'view_menu': True,
        'Scrobbles': Scrobbles,
        'average': math.ceil(int(Scrobbles)/nombre_jours),
        'view_search_bar': True
    })

@staff_member_required
def music_add_lyrics(request):
    repertoire = os.path.join(settings.BASE_DIR, 'static/lyrics')
    album = request.GET.get('album')
    track = request.GET.get('track')

    if request.method == 'POST':
        with open(f'{repertoire}/{album}-{track}.txt', "w") as f:
            f.write(request.POST.get('lyric'))

        return redirect('music:view-album', pk=album)

    context = {
        'album': models.Album.objects.get(pk=album),
        'track': models.Track.objects.get(pk=track)}

    return render(request, 'music/add_lyric.html', context)

@staff_member_required
def music_view_lyrics(request):
    repertoire = os.path.join(settings.BASE_DIR, 'static/lyrics')
    album = request.GET.get('album')
    track = request.GET.get('track')

    lyric = None

    with open(f'{repertoire}/{album}-{track}.txt', "r") as f:
       lyric = f.read()
    return render(request, 'music/view_lyric.html', {'lyric': lyric})

@staff_member_required
def view_review(request):
    repertoire = os.path.join(settings.BASE_DIR, 'static/review')
    album = request.GET.get('album')
    review = request.GET.get('review')
    return redirect('music:view-album', pk=album)

@staff_member_required
def view_album_by_code(request, pk):
    album = models.Album.objects.get(code=pk)

    return render(request, 'music/view_album.html', {'album': album})

class AlbumList(viewsets.ModelViewSet):

    queryset= models.Album.objects.all()
    serializer_class= serializers.AlbumSerializer
    permission_classes= (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = models.Album.objects.all().order_by('band__name', 'release_year')
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
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return self.serializer_class  # version plus restrictive
        return self.serializer_class

    def get_queryset(self):
        queryset = models.Track.objects.all()
        return queryset
    
    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     partial = kwargs.pop('partial', False)
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     if serializer.is_valid():
    #         track = serializer.save()
    #         print(track)
    #         return Response(track, status=status.HTTP_200_OK)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TrackListeningView(ViewSet):
    permission_classes= (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request):
        serializer = serializers.ListeningHistorySerializer(data=request.data)
        if serializer.is_valid():
            listening = serializer.save()
            return Response({"status": "success", "listening_id": listening.id})
        return Response(serializer.errors, status=400)
