from django.db import models
from django.template.defaultfilters import slugify
from game.models import Game

class Article(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    num_page = models.IntegerField()
    slug = models.SlugField(unique=True, blank=True)
    preface = models.TextField(max_length=1500)
    title_mag = models.CharField(max_length=40, blank=True)
    num_mag = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = f'{self.game.name} {self.game.system.slug} {self.title_mag} {self.num_mag}'
            self.slug = slugify(slug)
            super(Article, self).save(*args, **kwargs)
        else:
            super(Article, self).save(*args, **kwargs)


class Insert(models.Model):
    article = models.ForeignKey(Article, related_name='inserts', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=1000)
    id_num = models.IntegerField(blank=True, default=0)

    def __str__(self):
        if self.title is not None or self.title != '':
            return self.title
        else:
            return self.text[0:20]

    def save(self, *args, **kwargs):
        self.id_num = len(self.article.inserts.all())+1
        super(Insert, self).save(*args, **kwargs)


class Opinion(models.Model):
    article = models.ForeignKey(Article, related_name='opinions', on_delete=models.CASCADE, null=True)
    text = models.TextField(max_length=1500)
    tester = models.CharField(max_length=35)
    advice = models.CharField(max_length=25, blank=True)
    id_num = models.IntegerField(unique=True, default=0)

    def __str__(self):
        return f'{self.tester} - {self.text[0:40]}'

    def save(self, *args, **kwargs):
        self.id_num = len(self.article.opinions.all())+1
        super(Opinion, self).save(*args, **kwargs)


class Score(models.Model):
    article = models.ForeignKey(Article, related_name='scores', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    score = models.CharField(max_length=15)
    text = models.TextField(max_length=500, blank=True)


class Photo(models.Model):
    link = models.SlugField(max_length=100, null=False, blank=True, unique=True)
    text = models.TextField(max_length=500)
    id_num = models.IntegerField(blank=True, default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return self.link


class PhotoArticle(Photo):
    article = models.ForeignKey(Article, related_name='photos',on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        num = len(self.article.photos.all()) + 1
        self.id_num = num
        link = f'{self.article.game.name} {self.article.title_mag} {self.article.num_mag}_{num}'
        self.link = slugify(link)
        super(Photo, self).save(*args, **kwargs)


class PhotoInsert(Photo):
    insert = models.ForeignKey(Insert, related_name='photos', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        num = len(self.insert.photos.all()) + 1
        self.id_num = num
        link = f'encart {self.insert.id_num}_{num}'
        self.link = slugify(link)
        super(Photo, self).save(*args, **kwargs)


class Link(models.Model):
    article = models.ForeignKey(Article, related_name='links', on_delete=models.CASCADE)
    url = models.URLField(max_length=200)

    def __str__(self):
        return f'{self.url}'


class Paragraph(models.Model):
    article = models.ForeignKey(Article, related_name='paragraphs', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100, blank=True)
    text = models.TextField(max_length=2000)
    id_num = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return f'{self.article.game} - {self.text[0:70]}'
