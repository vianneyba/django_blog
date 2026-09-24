from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.conf import settings
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

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
		if not self.slug:
			self.slug = slugify(self.title)
		super().save(*args, **kwargs)

	def rename_content_file(self, old_slug):
		old_file = Path(settings.BASE_DIR) / "blog" / "articles" / f"{old_slug}.html"
		new_file = Path(settings.BASE_DIR) / "blog" / "articles" / f"{self.slug}.html"
		if old_file.exists():
			old_file.rename(new_file)

	def count_comments(self):
		return len(self.comment_set.all())

	def add_tag(self, tag):
		"""Ajoute un tag ou une liste de tags."""
		tags = tag if isinstance(tag, list) else [tag]
		self.tags.add(*tags)

	def get_content(self):
		"""Lit le contenu depuis le fichier HTML."""
		_file = Path(settings.BASE_DIR) / "blog" / "articles" / f"{self.slug}.html"
		if not _file.exists():
			return "<p>Pas de contenu pour cet article.</p>"
		return _file.read_text(encoding="utf-8")

	@property
	def content(self):
		"""Propriété qui lit le contenu du fichier"""
		return self.get_content()

	@content.setter
	def content(self, value):
		"""Setter optionnel pour sauvegarder le contenu"""
		self.save_content(value)

	def save_content(self, content):
		_file = Path(settings.BASE_DIR) / "blog" / "articles" / f"{self.slug}.html"
		_file.parent.mkdir(parents=True, exist_ok=True)
		try:
			_file.write_text(content, encoding="utf-8")
		except OSError as exc:
			logger.error("Impossible d'écrire %s : %s", _file, exc)
			raise

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Gestion de l\'article'
		verbose_name_plural = 'Gestion des articles'	
