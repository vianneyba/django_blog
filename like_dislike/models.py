from django.db import models
from blog.models import Article
from django.contrib.auth.models import User

class LikeArticle(models.Model):
    user = models.ForeignKey(User, verbose_name="Utilisateur", on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name="Article", on_delete=models.CASCADE)
    is_like = models.BooleanField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name= "Like - Dislike"

    def __str__(self):
        return f'{self.user} - {self.article.title} ({self.is_like})'