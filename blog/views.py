import re
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from slugify import slugify
from blog.models import Article, Category, Tag
from blog.permissions import ArticlePermissions
from blog import serializers
from blog.forms import ArticleForm
from comment.models import Comment
from comment.forms import CommentForm
from django.http import Http404
from django.contrib.auth.decorators import permission_required
from django.db import IntegrityError

def return_paginator(request, queryset):
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj

def return_article(request, slug=None, pk=None):
    """
    Fonction qui renvoie tous les elements d'un article (article, commentaire, like)
    slug        - slug de l'article
    pk          - id d'un article
    """
    context = {}

    try:
        if slug is not None:
            context['article'] = Article.objects.get(slug=slug)
        elif pk is not None:
            context['article'] = Article.objects.get(pk=pk)

        comments = Comment.objects.filter(article__id=context['article'].id)
        context['comments'] = return_paginator(request, comments)
    except ObjectDoesNotExist:
        return None

    if context['article'].published is False and context['article'].author != request.user:
        return None

    if (context['article'].like_count + context['article'].dislike_count) == 0:
        context['progress_bar'] = 50
    else:
        context['progress_bar'] = round(100 * (int(context['article'].like_count)/(context['article'].like_count+context['article'].dislike_count)))

    context['like'] = context['article'].search_like(request.user)

    return context

def index(request):
    """
    Page d'acceuil du blog
    return de tous les articles du blog qui sont publié
    """
    articles = Article.objects.all().filter(published=True)

    context = {
        'page_obj': return_paginator(request, articles),
        'articles': articles}
    return render(request, 'blog/index.html', context)

def by_slug(request, slug):
    """
    Page de vue d'un article du blog grace a son slug
    return l'article demandé avec le formulaire de commentaire
    """
    context = return_article(request, slug=slug)

    if context is None:
        raise Http404

    form_comment = CommentForm()

    context['form_comment'] = form_comment
    return render(request, 'blog/view-article.html', context)

def by_category(request, category):
    """
    Fonction qui envoie une liste d'article d'une catégorie
    category        -categorie recherché
    """
    articles = Article.objects.filter(category__slug=category, published=True)

    context = {
        'page_obj': return_paginator(request, articles),
        'articles': articles }
    return render(request, 'blog/index.html', context)

def by_tag(request, tag):
    """
    page qui liste les articles grace a ses tags
    return une liste d'article par rapport au tag qui sont publié
    tag         -string
    """
    articles = Article.objects.filter(tags__slug=tag, published=True)

    context = {'page_obj': return_paginator(request, articles), "articles": articles}
    return render(request, 'blog/index.html', context)

def by_author(request, author):
    """
    Fonction qui envoie une liste d'article d'un auteur
    author      -auteur recherché
    """
    if request.GET.get('view') == 'all' and author == request.user.username:
        articles = Article.objects.filter(author__username=author)
    else:
        articles = Article.objects.filter(author__username=author, published=True)

    if len(articles) == 0:
        raise Http404

    context = {'page_obj': return_paginator(request, articles), "articles": articles}
    return render(request, 'blog/index.html', context)

@permission_required("blog.add_article")
def add_article(request):
    """
    Fonction pour écrire un article
    """
    form_add_article = ArticleForm()
    if request.method == 'POST':
        form_add_article = ArticleForm(request.POST)
        if form_add_article.is_valid():
            article = form_add_article.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('blog:by-slug', slug=article.slug)

    context = {'form_add_article': form_add_article}
    return render(request, 'blog/add-article.html', context)

def search_category(category):
    """
    Fonction pour la création d'une catégorie
    """
    slug = slugify(category)
    category = Category.objects.get(slug=slug)
    return category.id

def search_tag(tags):
    """
    Fonction pour la création des tags et les ajoutes a un article
    tags        - string ex:'action;platform'
    """
    result= []
    for name in tags:
        slug = slugify(name)
        try:
            tag = Tag.objects.get(slug=slug)
            result.append(tag.pk)
        except ObjectDoesNotExist:
            tag = Tag(name=name, slug=slug)
            tag.save()
            result.append(tag.pk)
    return result


class ArticleViewset(ModelViewSet):
    permission_classes = (ArticlePermissions,)
    serializer_class = serializers.ArticleSerializer

    def get_queryset(self):
        return Article.objects.all().filter(published=True)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers.ArticleSaveSerializer
        return serializers.ArticleSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['author'] = request.user.id

        # Résolution category / tags avec gestion d'erreur
        try:
            data['category'] = search_category(data.get('category'))
            if 'tags' in data:
                data['tags'] = search_tag(data['tags'])
        except ValueError as exc:
            return Response(
                {'category': [str(exc)]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            article = serializer.save()
        except IntegrityError as e:
            return Response(
                {f"Contrainte violée : {e}"},
                status=status.HTTP_409_CONFLICT,
            )

        # Gestion du contenu APRÈS validation
        content = request.data.get('content')
        if content:
            article.save_content(content)

        return Response(
            serializers.ArticleSerializer(article).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Traitement spécial pour category et tags
        mutable_data = request.data.copy()
        mutable_data['author'] = self.request.user.id

        if 'category' in mutable_data:
            mutable_data['category'] = search_category(mutable_data['category'])

        if 'tags' in mutable_data:
            mutable_data['tags'] = search_tag(mutable_data['tags'])

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=mutable_data, partial=partial)
        if serializer.is_valid():
            article = serializer.save()
            content = self.request.data.get('content')
            if content:
                article.save_content(content)
            read_serializer = serializers.ArticleSerializer(article)
            return Response(read_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)