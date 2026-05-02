from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.conf import settings

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
	slug = models.SlugField( max_length=100, unique=True)
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
		_file = f'{settings.BASE_DIR}/blog/articles/{self.slug}.html'

		try:
			with open(_file, 'r') as out_file:
				return out_file.read()
		except FileNotFoundError:
			self.content= "<p>pas pe contenu pour cette article</p>"

		return None

	@property
	def content(self):
		"""Propriété qui lit le contenu du fichier"""
		return self.get_content()

	@content.setter
	def content(self, value):
		"""Setter optionnel pour sauvegarder le contenu"""
		self.save_content(value)

	def save_content(self, content):
		try:
			_file = f'{settings.BASE_DIR}/blog/articles/{self.slug}.html'
			with open(_file, 'x') as f:
				f.write(content)
		except FileExistsError:
			with open(_file, 'w') as f:
				f.write(content)
		except Exception as e:
			print(f"Erreur lors de la sauvegarde du contenu : {e}")
			raise

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Gestion de l\'article'
		verbose_name_plural = 'Gestion des articles'	
