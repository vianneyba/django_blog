from django.db import models
from django.template.defaultfilters import slugify
from game.models import Game

class Article(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    num_page = models.IntegerField()
    slug = models.SlugField(unique=True)
    preface = models.TextField(max_length=1500)
    title_mag = models.CharField(max_length=40, blank=True)
    num_mag = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return self.slug


class Insert(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=1000)

    def __str__(self):
        if self.title is not None or self.title != '':
            return self.title
        else:
            return self.text[0:20]


class Opinion(models.Model):
    game = models.ForeignKey(Article, on_delete=models.CASCADE)
    text = models.TextField(max_length=1500)
    tester = models.TextField(max_length=35)
    advice = models.TextField(max_length=25, blank=True)
    def __str__(self):
        return f'{self.tester} - {self.text[0:40]}'


class Score(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    score = models.CharField(max_length=15)
    text = models.TextField(max_length=500, blank=True)


class Photo(models.Model):
    link = models.SlugField(max_length=100, null=False, blank=True, unique=True)
    text = models.TextField(max_length=500)

    class Meta:
        abstract = True

    def __str__(self):
        return self.link

    def save(self, *args, **kwargs):
        print(f'------------>{self.link}')
        if not self.link:
            link = f'{self.article.game.name} {self.article.title_mag} {self.article.num_mag}_{len(self.article.photoarticle_set.all())+1}'
            self.link = slugify(link)
            print('on enregistre!')
            super(Photo, self).save(*args, **kwargs)
        else:
            super(Photo, self).save(*args, **kwargs)


class PhotoArticle(Photo):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class PhotoInsert(Photo):
    insert = models.ForeignKey(Insert, on_delete=models.CASCADE)


class Link(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    url = models.URLField(max_length=200)

    def __str__(self):
        return f'{self.url}'


class Paragraph(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100, blank=True)
    text = models.TextField(max_length=2000)

    def __str__(self):
        return f'{self.article.game} - {self.text[0:70]}'