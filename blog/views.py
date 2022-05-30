from django.shortcuts import render
from django.core.paginator import Paginator
from blog.models import Article
from comment.models import Comment

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