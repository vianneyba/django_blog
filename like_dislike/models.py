from django.db import models
from django.contrib.auth.models import User
from blog.models import Article
from comment.models import Comment

class Like(models.Model):
    user = models.ForeignKey(User, verbose_name="Utilisateur", on_delete=models.CASCADE, null=True, default=1)
    is_like = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class LikeArticle(Like):
    article = models.ForeignKey(Article, verbose_name="Article", on_delete=models.CASCADE)

    class Meta:
        verbose_name= "Like - Article"

    def __str__(self):
        return f'{self.user} - {self.article.title} ({self.is_like})'


class LikeComment(Like):
    comment = models.ForeignKey(Comment, verbose_name="Commentaire", on_delete=models.CASCADE)

    class Meta:
        verbose_name= "Like - Commentaire"

    def __str__(self):
        return f'{self.user} - {self.comment.content[:25]} ({self.is_like})'
