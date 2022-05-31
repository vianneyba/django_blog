from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from blog.models import Article
from like_dislike.models import LikeArticle

@login_required
def add_like(request):
    if request.GET.get('type') == 'article':
        article_pk = request.GET.get('pk')
        article = Article.objects.get(pk=article_pk)
        choice = request.GET.get('choice')

        try:
            like = LikeArticle.objects.get(user=request.user, article=article)
            if choice == 'true':
                if like.is_like is not True:
                    article.like_count += 1
                    article.dislike_count -= 1
                    like.is_like = True
            else:
                if like.is_like is True:
                    article.like_count -= 1
                    article.dislike_count += 1
                    like.is_like = False

        except ObjectDoesNotExist:
            like = LikeArticle(user=request.user, article=article)
            if choice == 'true':
                article.like_count += 1
                like.is_like = True
            else:
                article.dislike_count += 1
                like.is_like = False

        like.save()
        article.save()

    return redirect('blog:by-slug', slug=article.slug)
