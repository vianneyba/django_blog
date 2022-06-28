import os
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from game.models import Game, System
from game import serializers

@staff_member_required
def list_game(request):
    url =''
    games_list = Game.objects.all()

    if 'system' in request.GET and request.GET["system"] != '':
        url += f'&system={request.GET["system"]}'
        games_list = games_list.filter(system__slug=request.GET["system"])
    if 'search' in request.GET and request.GET["search"] != '':
        url += f'&search={request.GET["search"]}'
        games_list = games_list.filter(name__icontains=request.GET["search"])

    paginator = Paginator(games_list, 25)

    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'game_view.html',
        {'page_obj': page_obj, 'url': url})

@staff_member_required
def run_game(request, pk):
    path_core = '/usr/lib/x86_64-linux-gnu/libretro/'
    game = Game.objects.get(pk=pk)
    command_line = game.get_command_line()
    print(command_line)
    os.system(command_line)

    return HttpResponse("Hello, world. You're at the polls index.")

class GamesViewset(ModelViewSet):
    serializer_class = serializers.GameSerializer
    queryset = Game.objects.all()

    def retrieve(self, request, pk=None):
        queryset = Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        serializer = serializers.GameSerializer(game)
        return Response(serializer.data)

    def list(self, request):
        queryset = Game.objects.all()
        slug_system = request.query_params.get('system', None)
        name_game = request.query_params.get('game', None)

        if slug_system is not None:
            queryset = queryset.filter(system__slug=slug_system)
        if name_game is not None:
            queryset = queryset.filter(name__icontains=name_game)

        serializer = serializers.GameSerializer(queryset, many=True)
        return Response(serializer.data)

class SystemsViewset(ModelViewSet):
    serializer_class = serializers.SystemSerializer
    queryset = System.objects.all()