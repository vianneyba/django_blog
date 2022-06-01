from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from blog.models import Article
from comment.models import Comment
from like_dislike.models import LikeArticle, LikeComment

@login_required
def add_like(request):
    pk = request.GET.get('pk')
    if request.GET.get('type') == 'article':
        article = Article.objects.get(pk=pk)
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
    
    if request.GET.get('type') == 'comment':
        comment = Comment.objects.get(pk=pk)
        choice = request.GET.get('choice')

        try:
            like = LikeComment.objects.get(user=request.user, comment=comment)
            if choice == 'true':
                if like.is_like is not True:
                    comment.like_count += 1
                    comment.dislike_count -= 1
                    like.is_like = True
            else:
                if like.is_like is True:
                    comment.like_count -= 1
                    comment.dislike_count += 1
                    like.is_like = False

        except ObjectDoesNotExist:
            like = LikeComment(user=request.user, comment=comment)
            if choice == 'true':
                comment.like_count += 1
                like.is_like = True
            else:
                comment.dislike_count += 1
                like.is_like = False

        like.save()
        comment.save()

    return redirect(request.META.get('HTTP_REFERER'))
