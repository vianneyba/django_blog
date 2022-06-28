from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
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
    albums = models.Album.objects.all()
    if request.GET.get('date'):
        release_year = request.GET.get('date')
        albums = albums.filter(release_year=release_year)
    if request.GET.get('band'):
        band = request.GET.get('band')
        albums = albums.filter(band=band)
    
    context = {'page_obj': return_paginator(request, albums)}
    return render(request, 'music/index.html', context)

@staff_member_required
def view_album(request, pk):
    album = models.Album.objects.get(pk=pk)

    return render(request, 'music/view_album.html', {'album': album})

class AlbumList(viewsets.ModelViewSet):

    queryset= models.Album.objects.all()
    serializer_class= serializers.AlbumSerializer
    permission_classes= (permissions.IsAuthenticatedOrReadOnly,)