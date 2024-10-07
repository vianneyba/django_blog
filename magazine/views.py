from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.http import HttpResponse, Http404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from magazine import models
from game.models import Game, System
from magazine import forms
from magazine import serializers
from magazine.convert_ini import Template, Export
from blog.create_blog import Blog_Article
import random
import os
from magazine.import_from_am import import_page

@permission_required("magazine.view_article")
def view_article(request, my_type, pk):
    """
    fonction qui récupére le test en base de donnée et le contenu dans le fichier html
    """
    article = models.Article.objects.get(pk=pk)

    file = open(f"magazine/articles/{article.my_id}.html", "r")
    content = file.read()
    file.close()

    context = {'article': article, 'content': content, 'view_menu': False}
    return render(request, "magazine/view-article-finish.html", context)

@permission_required("magazine.view_article")
def view_page(request):
    """
    Fonction de recherche d'une page de test dans la base pour la modifier
    get:num, get: mag
    get:article
    get:type=random
    """
    if request.method == 'POST':
        pk = request.POST['pk']
        test = models.Page.objects.get(pk=pk)
        if "dupliquer" in request.POST:
            test.pk = None

        test.title_game = request.POST['title_game']
        test.type_art = request.POST['type_article']
        if request.POST['game_id'] != 'None':
            test.game_id = request.POST['game_id']
        test.save()

    if "article" in request.GET:
        pk = request.GET["article"]
        try:
            article = models.Page.objects.get(pk=pk)
        except:
            article = None
    elif "type" in request.GET and request.GET["type"] == 'random':
        items = list(models.Page.objects.all())
        article = random.choice(items)
    elif "mag" in request.GET and "num" in request.GET:
        mag = request.GET['mag']
        num = request.GET['num']
        try:
            magazine = models.Magazine.objects.get(title_mag=mag,num_mag=num)
            article = magazine.page_set.all().filter(title_game='')[0]
        except IndexError:
            response = redirect('magazine:view-magazine')
            response['Location'] += f'?mag={mag}&num={num}'
            return response
        except ObjectDoesNotExist:
            article = None
    else:
        try:
            article = models.Page.objects.filter(title_game='\n')[0]
        except:
            article = None

    context = {'article': article}
    return render(request, 'magazine/view-page.html', context)

@permission_required("magazine.add_article")
def add_article(request):
    form = forms.ArticleForm()

    if request.method == 'POST':
        form = forms.ArticleForm(request.POST)
        if form.is_valid():
            
            article = form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form}
    return render(request, 'magazine/write-article.html', context)

@permission_required("magazine.add_article")
def export(request):
    article = None
    if 'code' in request.GET:
        code = request.GET.get('code')
        my_doc = Export(models.Article)
        my_doc.read_file(code)
        my_doc.create_article()
        article = my_doc.article


    return render(request, 'magazine/export.html', {'article': article})

@permission_required("magazine.view_article")
def list_articles(request):
    """
    Fonction qui liste tous les tests
    """
    articles = models.Article.objects.all()

    context = {'articles': articles, 'view_menu': False}
    return render(request, 'magazine/list-articles.html', context)

@permission_required("magazine.add_article")
def update_article(request, my_id):
    file = open(f"magazine/article/{my_id}.ini", "r")
    content = file.read()

    context = {"text": content, "button": "Update", "my_id": my_id}
    return render(request, 'magazine/write-new-article.html', context)

@permission_required("magazine.add_article")
def write_article(request):
    if request.method == 'POST':
        my_doc = Export(models.Article)
        if "my_id" in request.POST:
            my_doc.write_file(request.POST['my_id'], request.POST['ini'])
        else:
            my_doc.create_ini(request.POST['ini'])

        url = reverse("magazine:view-article-by-name", args=(my_doc.config['info']['id'],))
        return redirect(url)

    txt = "[info]\n"
    txt += "id = \n"
    txt += "\n"
    txt += "[jeux]\n"
    txt += "id_sc = \n"
    txt += "title = \n"
    txt += "support = \n"
    txt += "tags = \n"
    txt += "core = \n"
    txt += "\n"
    txt += "[magazine]\n"
    txt += "title = \n"
    txt += "numero = \n"
    txt += "mois = \n"
    txt += "link = \n"
    txt += "\n"
    txt += "[article]\n"
    txt += "category = \n"
    txt += "type = \n"
    txt += "preface = \n"
    txt += "links = \n"
    txt += "template = \n"
    txt += "\n"
    txt += "[paragraphes]\n"
    txt += "1 = \n"
    txt += "2 = \n"
    txt += "\n"
    txt += "[avis]\n"
    txt += "1 = \n"
    txt += "2 = \n"
    txt += "\n"
    txt += "[notes]\n"
    txt += "Animation = \n"
    txt += "Bruitage = \n"
    txt += "Graphisme = \n"
    txt += "Intérêt = \n"
    txt += "\n"
    txt += "[photos]\n"
    txt += "1 = \n"
    txt += "2 = \n"

    context = {'text': txt, 'button': 'Nouveau'}
    return render(request, 'magazine/write-new-article.html', context)
 
@staff_member_required
def import_mag(request, id_mag, title_mag, num_mag):
    magazine = import_page(models, id_mag, title_mag, num_mag)
    return render(request, 'magazine/view-magazine.html', {'magazines': [magazine]})

def search_article(request):
    """
    Fonction qui recherche un test dans un magazine
    post:url==      - recherche par l'url du test
    """
    context = {}
    if request.method == 'POST':
        if 'url==' in request.POST['search']:
            url = request.POST['search'][5:]
            tests = models.Page.objects.filter(url=url)
        else:
            search = request.POST['search']
            tests = models.Page.objects.filter(title_game__contains=search)
        
        context['articles'] = tests

    return render(request, 'magazine/view-list.html', context)

def view_magazine(request):
    """
    Fonction qui liste les tests de magazine
    get:mag         -nom du magazine
    get:num         -numero du magazine
    """
    search = {}

    if 'mag' in request.GET:
        search['title_mag'] = request.GET['mag']
    if 'num' in request.GET:
        search['num_mag'] = request.GET['num']

    magazines = models.Magazine.objects.filter(**search)
    return render(request, 'magazine/view-magazine.html', {'magazines': magazines})       