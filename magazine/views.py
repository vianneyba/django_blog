from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify
from django.db import IntegrityError
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from magazine.models import Article, Insert
from magazine import forms
from magazine import serializers


def view(request, slug):
    article = Article.objects.get(slug=slug)

    template = f'magazine/article/{article.slug}.html'
    context = {'article': article, 'template': template}
    return render(request, "magazine/view-article-finish.html", context)


def write_article(request):
    form = forms.ArticleForm()

    if request.method == 'POST':
        form = forms.ArticleForm(request.POST)
        if form.is_valid():
            article = form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form}
    return render(request, 'magazine/write-article.html', context)


def add_paragraph(request, pk):
    article = Article.objects.get(id=pk)
    form = forms.ParagraphForm(initial={'article': article.id})

    if request.method == 'POST':
        form = forms.ParagraphForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-paragraph.html', context)


def add_photo(request, pk):
    article = Article.objects.get(id=pk)
    form = forms.PhotoForm(initial={'article': article.id})

    if request.method == 'POST':
        form = forms.PhotoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-photo.html', context)


def add_photo_insert(request, pk, pk_insert):
    article = Article.objects.get(id=pk)
    insert = Insert.objects.get(id=pk_insert)

    form = forms.PhotoInsertForm(initial={'insert': insert.id})

    if request.method == 'POST':
        form = forms.PhotoInsertForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article, 'insert': insert}
    return render(request, 'magazine/add-insert-photo.html', context)


def add_insert(request, pk):
    article = Article.objects.get(id=pk)
    form = forms.InsertForm(initial={'article': article.id})

    if request.method == 'POST':
        form = forms.InsertForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-insert.html', context)


def add_link(request, pk):
    article = Article.objects.get(id=pk)
    form = forms.LinkForm(initial={'article': article.id})

    if request.method == 'POST':
        form = forms.LinkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-link.html', context)


def add_score(request, pk):
    article = Article.objects.get(id=pk)
    form = forms.ScoreForm(initial={'article': article.id})

    if request.method == 'POST':
        form = forms.ScoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-score.html', context)


def add_opinion(request, pk):
    article = Article.objects.get(id=pk)
    form = forms.OpinionForm(initial={'article': article.id})

    if request.method == 'POST':
        form = forms.OpinionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-opinion.html', context)


def view_article(request, pk):
    article = Article.objects.get(id=pk)
    context = {'article': article}

    return render(request, 'magazine/view-article.html', context)

class ArticleList(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = serializers.ArticleSerializer
    # permission_classes= (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        tempdict = request.data.copy()
        serializer = serializers.ArticleSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    'Existe déja',
                    status=status.HTTP_409_CONFLICT)
