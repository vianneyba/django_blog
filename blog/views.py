from django.shortcuts import render
from django.core.paginator import Paginator
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from blog.models import Article, Category
from blog.permissions import ArticlePermissions
from comment.models import Comment
from blog import serializers

def return_paginator(request, queryset):
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj

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
    article = Article.objects.get(slug=slug)
    Comments = Comment.objects.filter(article__slug=slug)

    context= {
        'article': article,
        'comments': return_paginator(request, Comments)}
    return render(request, 'blog/view-article.html', context)

def by_author(request, author):
    articles = Article.objects.filter(author__username=author)

    context = {'page_obj': return_paginator(request, articles)}
    return render(request, 'blog/index.html', context)

class ArticleViewset(ModelViewSet):
    permission_classes = (ArticlePermissions,)
    serializer_class = serializers.ArticleSerializer

    def get_queryset(self):
        return Article.objects.all().filter(published=True)

    # @permission_classes(IsAdminUser)
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