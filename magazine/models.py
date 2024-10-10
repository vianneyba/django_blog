from django.db import models
from django.template.defaultfilters import slugify
from game.models import Game
from magazine.convert_ini import Template
import os


TYPE_CHOICES = [
    ('test', 'test'), ('preview', 'preview'), ('annonce', 'annonce'), ('pub', 'pub'), ('dossier', 'dossier'), ('autre', 'autre')
]


class Article(models.Model):
    title = models.TextField(max_length=80)
    system = models.TextField(max_length=40, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    preface = models.TextField(max_length=1700)
    my_id = models.CharField(max_length=16, blank=True)
    title_mag = models.CharField(max_length=40, blank=True)
    num_mag = models.IntegerField(blank=True, default=0)
    type_art = models.CharField(max_length=10, choices=TYPE_CHOICES, default='test')

    def __str__(self):
        return f"{self.slug} - {self.preface[0:60]}"

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = f'{self.title} {self.system} {self.title_mag} {self.num_mag}'
            self.slug = slugify(slug)
            super(Article, self).save(*args, **kwargs)
        else:
            super(Article, self).save(*args, **kwargs)

    # def num_page(self):
    #     return len(self.links.all())

    def view(self):
        try:
            return self.template.return_template()
        except AttributeError:
            self.template = Template(self.my_id)
            return self.template.return_template()

    # def title(self):
    #     try:
    #         return self.template.create_title("texte")
    #     except AttributeError:
    #         self.template = Template(self.my_id)
    #         return self.template.create_title("texte")

    # def link(self):
    #     try:
    #         return self.template.create_link()
    #     except AttributeError:
    #         self.template = Template(self.my_id)
    #         return self.template.create_link()

    # def export_pelican(self):
    #     try:
    #         return self.template.export_pelican()
    #     except AttributeError:
    #         self.template = Template(self.my_id)
    #         return self.template.export_pelican()

    class Meta:
        # ordering = ['game__name']
        verbose_name = 'Gestion de l\'article'
        verbose_name_plural = 'Gestion des articles'

class Magazine(models.Model):
    url = models.URLField(unique=True, max_length=150)
    title_mag = models.CharField(max_length=40)
    num_mag = models.IntegerField()

    def __str__(self):
        return f"{self.title_mag} - {self.num_mag}"

class Page(models.Model):
    title_game = models.TextField(max_length=80)
    game_id = models.IntegerField(null=True)
    url = models.URLField(max_length=300)
    type_art = models.CharField(max_length=10, choices=TYPE_CHOICES, default='autre')
    magazine = models.ForeignKey(Magazine, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title_game} dans {self.magazine.title_mag} numéro {self.magazine.num_mag} ({self.url})"
    
    def image(self):
        return os.path.basename(self.url)