from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from music import models, serializers

def return_paginator(request, queryset):
    paginator = Paginator(queryset, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj

@staff_member_required
def index(request):
    albums = models.Album.objects.all().order_by('-pk')
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
    
    context = {'page_obj': return_paginator(request, albums)}
    return render(request, 'music/index.html', context)

@staff_member_required
def view_album(request, pk):
    album = models.Album.objects.get(pk=pk)

    return render(request, 'music/view_album.html', {'album': album})

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