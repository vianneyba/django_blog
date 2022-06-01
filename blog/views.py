from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from slugify import slugify
from blog.models import Article, Category, Tag
from blog.permissions import ArticlePermissions
from blog import serializers
from blog.forms import ArticleForm
from comment.models import Comment
from comment.forms import CommentForm

def return_paginator(request, queryset):
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj

def return_article(request, slug=None, pk=None):
    try:
        if slug is not None:
            article = Article.objects.get(slug=slug)
        elif pk is not None:
            article = Article.objects.get(pk=pk)

        Comments = Comment.objects.filter(article__id=article.id)
    except ObjectDoesNotExist:
        return None

    if article.published is False and article.author != request.user:
        return None

    if (article.like_count+article.dislike_count) == 0:
        progress_bar = 50
    else:
        progress_bar= round(100 * (int(article.like_count)/(article.like_count+article.dislike_count)))

    return {
        'article': article,
        'comments': return_paginator(request, Comments),
        'progress_bar': progress_bar,
        'like': article.search_like(request.user)}

def index(request):
    articles = Article.objects.all().filter(published=True)

    context = {'page_obj': return_paginator(request, articles)}
    return render(request, 'blog/index.html', context)

def by_category(request, category):
    articles = Article.objects.filter(category__slug=category)

    context = {'page_obj': return_paginator(request, articles)}
    return render(request, 'blog/index.html', context)

def by_tag(request, tag):
    articles = Article.objects.filter(tags__slug=tag)

    context = {'page_obj': return_paginator(request, articles)}
    return render(request, 'blog/index.html', context)

def by_slug(request, slug):
    context = return_article(request, slug=slug)
    if context is None:
        return redirect('blog:index')

    form_comment = CommentForm()
    form_comment.fields["article_id"].initial = context['article'].id

    context['form_comment'] = form_comment
    return render(request, 'blog/view-article.html', context)

def by_author(request, author):
    if request.GET.get('view') == 'all' and author == request.user.username:
        articles = Article.objects.filter(author__username=author)
    else:
        articles = Article.objects.filter(author__username=author, published=True)

    context = {'page_obj': return_paginator(request, articles)}
    return render(request, 'blog/index.html', context)

def add_article(request):
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

def update_article(request, pk):
    article = Article.objects.get(pk=pk)
    form_add_article = ArticleForm(instance=article)

    if request.method == 'POST':
        form_add_article = ArticleForm(request.POST, instance=article)
        if form_add_article.is_valid():
            form_add_article.save()
            return redirect('blog:by-slug', slug=article.slug)
        
     
    context = {
        'article': article,
        'form_add_article': form_add_article,
        'type': 'update'}
    return render(request, 'blog/add-article.html', context)

def publish_article(request, pk, value):
    if value == 'True':
        published = True
    else:
        published = False
    article = Article.objects.get(pk=pk)
    if article.author == request.user:
        article.published = published
        article.save()

    return redirect('blog:index')
    

class ArticleViewset(ModelViewSet):
    permission_classes = (ArticlePermissions,)
    serializer_class = serializers.ArticleSerializer

    def get_queryset(self):
        return Article.objects.all().filter(published=True)

    def create(self, request, *args, **kwargs):
        tempdict = request.data.copy()
        tempdict['author'] = self.request.user.id

        category = Category.objects.get(slug=tempdict['category'])
        tempdict['category'] = category.id

        serializer = serializers.ArticleSaveSerializer(data=tempdict)
        if serializer.is_valid():
            article = serializer.save()
            return Response(self.serializer_class(article).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)