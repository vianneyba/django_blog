import re
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils import timezone
from magazine.models import Article


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
	title = models.CharField('Titre:', max_length=100)
	slug = models.SlugField(unique=True)
	created_at = models.DateTimeField(default=timezone.now)
	published = models.BooleanField(default=False)
	update_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	like_count = models.IntegerField(default=0)
	dislike_count = models.IntegerField(default=0)
	tags = models.ManyToManyField(Tag)
	banner = models.URLField(blank=True)

	def __str__(self):
		return self.title

	def search_like(self, user):
		likes = self.likearticle_set.all()
		for like in likes:
			if like.user == user:
				return like
		return None

	def save(self, *args, **kwargs):
		slug = f'{self.title}'
		self.slug = slugify(slug)
		super(Article, self).save(*args, **kwargs)

	def count_comments(self):
		return len(self.comment_set.all())

	def add_tag(self, tag):
		if isinstance(tag, list):
			for t in tag:
				self.tags.append(t)
			else:
				self.tags.append(tag)

	def get_content(self):
		_file = f'/home/vianney/Documents/programme/django_blog/blog/articles/{self.slug}.html'

		try:
			with open(_file, 'r') as out_file:
				self.content = out_file.read()
		except FileNotFoundError:
			self.content= "<p>pas pe contenu pour cette article</p>"

		return self.content

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Gestion de l\'article'
		verbose_name_plural = 'Gestion des articles'
