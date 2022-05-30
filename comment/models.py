from django.db import models
from django.contrib.auth.models import User
from blog.models import Article
from django.utils import timezone


class Comment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	content = models.TextField()
	created_at = models.DateTimeField(default=timezone.now)
	article = models.ForeignKey(Article, on_delete=models.CASCADE)

	def __str__(self):
		return self.content[0:25]

	class Meta:
		verbose_name = 'Gestion du commentaire'
		verbose_name_plural = 'Gestion des commentaires'
