from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify
from django.db import IntegrityError
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from magazine import models
from game.models import Game, System
from game.serializers import GameSerializer
from magazine import forms
from magazine import serializers


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


def view_article(request, pk):
    article = models.Article.objects.get(id=pk)
    context = {'article': article}

    return render(request, 'magazine/view-article.html', context)


def list_articles(request):
    articles = models.Article.objects.all()

    context = {'articles': articles, 'view_menu':False}
    return render(request, 'magazine/list-articles.html', context)


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
