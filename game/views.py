import os
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from game.models import Game
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
    games = paginator.get_page(page)
    return render(request, 'game_view.html',
        {'games': games, 'url': url})

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
        user = get_object_or_404(queryset, pk=pk)
        serializer = serializers.GameSerializer(user)
        return Response(serializer.data)