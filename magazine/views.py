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
import re
from magazine.import_from_am import import_page
from django.templatetags.static import static
from django.conf import settings

@permission_required("magazine.view_article")
def view_article(request, m_type, pk):
    """
    fonction qui récupére le test en base de donnée et le contenu dans le fichier html ou ini
    """
    article = models.Article.objects.get(pk=pk)
    try:
        file = open(f"magazine/articles/{article.my_id}.html", "r")
        content = file.read()
        file.close()
    except FileNotFoundError:
        my_doc = Export(models.Article)
        my_doc.read_file(article.my_id)
        my_doc.create_article()
        content = my_doc.article.view()

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
def ini_to_html(request):
    article = None
    if 'code' in request.GET:
        code = request.GET.get('code')
        my_doc = Template(code, models.Article)
        my_doc.return_template()
        article = "my_doc.article"

    context = {
        'content': my_doc.article.template,
        'article': my_doc.article}

    return render(request, 'magazine/export.html', context)

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
    file = open(f"magazine/articles/{my_id}.ini", "r")
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
    post:code==     - recherche le fichier ini
    """
    context = {}
    if request.method == 'POST':
        if 'url==' in request.POST['search']:
            url = request.POST['search'].replace('url==', '')
            tests = models.Page.objects.filter(url=url)
        elif 'code==' in request.POST['search']:
            # return redirect('magazine:import-mag')
            response = redirect('magazine:ini-to-html')
            response['Location'] += '?code='+request.POST['search'].replace('code==', '')
            return response
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

def scan(request):
    result = ""
    dir_scans = f"{settings.STATICFILES_DIRS[0]}/scans"

    context = {'type': 'mag'}
    context['magazines']= []

    if request.method == 'POST':
        path= request.GET['path']
        pattern = re.compile('([a-zA-Z+ ]+)_([0-9]{3})')
        match = pattern.search(path)
        try:
            magazine = models.Magazine.objects.get(url=request.POST['path'])
        except ObjectDoesNotExist:
            magazine = models.Magazine.objects.create(
                url=request.POST['path'],
                title_mag=match.group(1),
                num_mag=match.group(2))

        title_game = request.POST['title_game']


    if "path" in request.GET:
        context['type'] = "page"
        context['magazines'] = create_n(request.GET['path'], dir_scans)

    for x in os.listdir(dir_scans):
        context['magazines'].append(x)
    # return HttpResponse(f"{result}")

    # if request.method == 'POST':
    #     name_img = request.POST['image']
    #     p = re.compile('([a-zA-Z+ ]+)_([0-9]{3})_[0-9]{2,3}.avif')
    #     m = p.search(name_img)


    #     new_entry = models.Page.objects.create(
    #         title_game=title_game,
    #         url=request.POST['path_image'],
    #         magazine=magazine,
    #         type_art=request.POST['type_art'])

    # context = {'type': 'mag'}
    # directory = f"{settings.STATICFILES_DIRS[0]}/scans/"

    # if "path" in request.GET:
    #     dir_mag = request.GET['path'].replace("%20", " ")
    #     context['directory_image'] = static(f"/scans/{link}")
    #     context['magazines'] = create_n(dir_mag ,directory, context['directory_image'])
    #     directory = f"{directory}{link}"
    #     context['path'] = directory
    #     context['type'] = "page"


    # context['magazines'] = []


    return render(request, 'magazine/page_scan.html', context)

def create_n(path, dir_scans):
    pages = []
    pattern = re.compile('([a-zA-Z+ ]+)_([0-9]{3})')
    match = pattern.search(path)

    try:
        magazine = models.Magazine.objects.get(url=f"{dir_scans}/{path}")
    except:
        magazine = models.Magazine.objects.create(
            url=f"{dir_scans}/{path}",
            title_mag=match.group(1),
            num_mag=match.group(2))

    for link_image in sorted(os.listdir(f"{dir_scans}/{path}")):
        try:
            link_image = static(f"/scans/{path}/{link_image}")
            page = models.Page.objects.get(url=link_image)
        except:
            page = models.Page(
                title_game="",
                url=link_image,
                magazine=magazine,
                type_art="autre")

        pages.append(page)

    return pages
