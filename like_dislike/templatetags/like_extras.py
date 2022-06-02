from django.core.exceptions import ObjectDoesNotExist
from django import template
from django.contrib.auth.models import User
from blog.models import Article
from comment.models import Comment

register = template.Library()
register.simple_tag()

@register.simple_tag
def disabled_link(likable_id, user, type_like, is_like):
    if type_like == 'article':
        try:
            like = user.likearticle_set.get(article_id=likable_id)
        except ObjectDoesNotExist:
            return ''
    elif type_like == 'comment':
        try:
            like = user.likecomment_set.get(comment_id=likable_id)
        except ObjectDoesNotExist:
            return ''

    if like.is_like == is_like:
        return 'disabled-link'
    return ''