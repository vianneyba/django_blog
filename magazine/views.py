from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from magazine import models
from game.models import Game, System
from magazine import forms
from magazine import serializers
from magazine.convert_ini import Template, Export
from blog.create_blog import Blog_Article

def view(request, slug):
    article = models.Article.objects.get(slug=slug)

    template = f'magazine/article/{article.slug}.html'
    context = {'article': article, 'template': template, 'view_menu': False}
    return render(request, "magazine/view-article-finish.html", context)


def add_article(request):
    form = forms.ArticleForm()

    if request.method == 'POST':
        form = forms.ArticleForm(request.POST)
        if form.is_valid():
            
            article = form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form}
    return render(request, 'magazine/write-article.html', context)


def add_paragraph(request, pk):
    article = models.Article.objects.get(id=pk)
    form = forms.ParagraphForm(initial={'article': article.id})

    if request.method == 'POST':
        form = forms.ParagraphForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-paragraph.html', context)

def add_photo(request, pk):
    article = models.Article.objects.get(id=pk)
    form = forms.PhotoForm(initial={'article': article.id})

    if request.method == 'POST':
        form = forms.PhotoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-photo.html', context)

def add_photo_insert(request, pk, pk_insert):
    article = models.Article.objects.get(id=pk)
    insert = models.Insert.objects.get(id=pk_insert)

    form = forms.PhotoInsertForm(initial={'insert': insert.id})

    if request.method == 'POST':
        form = forms.PhotoInsertForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article, 'insert': insert}
    return render(request, 'magazine/add_insert_photo.html', context)

def add_insert(request, pk):
    article = models.Article.objects.get(id=pk)
    form = forms.InsertForm(initial={'article': article.id})

    if request.method == 'POST':
        form = forms.InsertForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-insert.html', context)

def add_link(request, pk):
    article = models.Article.objects.get(id=pk)
    form = forms.LinkForm(initial={'article': article.id})

    if request.method == 'POST':
        form = forms.LinkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-link.html', context)

def add_score(request, pk):
    article = models.Article.objects.get(id=pk)
    form = forms.ScoreForm(initial={'article': article.id})

    if request.method == 'POST':
        form = forms.ScoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-score.html', context)

def add_opinion(request, pk):
    article = models.Article.objects.get(id=pk)
    form = forms.OpinionForm(initial={'article': article.id})

    if request.method == 'POST':
        form = forms.OpinionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-opinion.html', context)

def view_article(request, my_type, pk):
    if my_type == 'id':
        article = models.Article.objects.get(id=pk)

    context = {'article': article, 'view_menu': False}

    return render(request, 'magazine/view-article-name.html', context)

def view_article_by_name(request, name):

    template = Template(name)

    # context = {'template': my_module.template, 'article':my_module.article, 'view_menu': False}
    context = {'template': template.return_template(), 'my_id': template.config['info']['id']}

    return render(request, 'magazine/view-article-name.html', context)

def export(request):
    article = None
    if 'code' in request.GET:
        code = request.GET.get('code')
        my_doc = Export(models.Article)
        my_doc.read_file(code)
        my_doc.create_article()
        article = my_doc.article


    return render(request, 'magazine/export.html', {'article': article})


def list_articles(request):
    articles = models.Article.objects.all()

    context = {'articles': articles, 'view_menu': False}
    return render(request, 'magazine/list-articles.html', context)


def update_article(request, my_id):
    file = open(f"magazine/article/{my_id}.ini", "r")
    content = file.read()

    context = {"text": content, "button": "Update", "my_id": my_id}
    return render(request, 'magazine/write-new-article.html', context)


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


class ArticleList(viewsets.ModelViewSet):
    permission_classes= (permissions.IsAuthenticatedOrReadOnly,)
    queryset = models.Article.objects.all()
    serializer_class = serializers.ArticleSerializer

    def create(self, request, *args, **kwargs):
        system_1 = request.data['article']['game']['system']
        try:
            system = System.objects.get(slug=system_1['slug'])
        except ObjectDoesNotExist:
            system = System(title=system_1['title'], slug=system_1['slug'])
            system.save()

        game_1 = request.data['article']['game']
        try:
            game = Game.objects.get(name=game_1['name'], system=system)
        except ObjectDoesNotExist:
            game = Game(name=game_1['name'], system=system)
            game.save()

        article_1 = request.data['article']
        try:
            slug = f'{game.name} {game.system.slug} {article_1["title_mag"]} {article_1["num_mag"]}'
            article = models.Article.objects.get(slug=slugify(slug))
        except  ObjectDoesNotExist:
            article = models.Article(preface=article_1['preface'], title_mag=article_1['title_mag'], num_mag=article_1['num_mag'])
            article.game = game
            article.save()

        for paragraph_1 in article_1['paragraphs']:
            paragraph = models.Paragraph(text=paragraph_1['text'], article=article)
            paragraph.save()

        for link_1 in article_1['links']:
            link = models.Link(url=link_1['url'], article=article)
            link.save()

        for photo_1 in article_1['photoArticle']:
            photo = models.PhotoArticle(text=photo_1['text'], article=article)
            photo.save()

        for insert_1 in article_1['inserts']:
            insert = models.Insert(title=insert_1['title'], text=insert_1['text'], article=article)
            insert.save()

            if 'photoInserts' in insert_1:
                for photo_1 in insert_1['photoInserts']:
                    photo = models.PhotoInsert(text=photo_1['text'] ,insert=insert)
                    photo.save()

        for opinion_1 in article_1['opinions']:
            opinion = models.Opinion(
                tester=opinion_1['tester'],
                text=opinion_1['text'],
                advice=opinion_1['advice'],
                article=article)
            opinion.save()

        for score_1 in article_1['scores']:
            score = models.Score(
                title=score_1['title'],
                text=score_1['text'],
                score=score_1['score'],
                article=article)
            score.save()

        serializers_1 = serializers.ArticleSerializer(article)
        return Response(
                    serializers_1.data,
                    status=status.HTTP_201_CREATED)