from django.db import models
from django.template.defaultfilters import slugify
from game.models import Game
from magazine.convert_ini import Template


TYPE_CHOICES = [
    ('test', 'test'), ('preview', 'preview'), ('annonce', 'annonce')
]


class Article(models.Model):
    # game = models.ForeignKey(Game, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)
    preface = models.TextField(max_length=1700)
    my_id = models.CharField(max_length=16, blank=True)
    # title_mag = models.CharField(max_length=40, blank=True)
    # num_mag = models.IntegerField(blank=True, default=0)
    type_art = models.CharField(max_length=10, choices=TYPE_CHOICES, default='test')

    def __str__(self):
        return f"{self.slug} - {self.preface[0:30]}"

    def save(self, *args, **kwargs):
        if not self.slug:
            # slug = f'{self.game.name} {self.game.system.slug} {self.title_mag} {self.num_mag}'
            # self.slug = slugify(slug)
            super(Article, self).save(*args, **kwargs)
        else:
            super(Article, self).save(*args, **kwargs)

    def num_page(self):
        return len(self.links.all())

    def view(self):
        try:
            return self.template.return_template()
        except AttributeError:
            self.template = Template(self.my_id)
            return self.template.return_template()

    def title(self):
        try:
            return self.template.create_title("texte")
        except AttributeError:
            self.template = Template(self.my_id)
            return self.template.create_title("texte")

    def link(self):
        try:
            return self.template.create_link()
        except AttributeError:
            self.template = Template(self.my_id)
            return self.template.create_link()

    def export_pelican(self):
        try:
            return self.template.export_pelican()
        except AttributeError:
            self.template = Template(self.my_id)
            return self.template.export_pelican()

    class Meta:
        # ordering = ['game__name']
        verbose_name = 'Gestion de l\'article'
        verbose_name_plural = 'Gestion des articles'


class Insert(models.Model):
    article = models.ForeignKey(Article, related_name='inserts', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=1000)
    id_num = models.IntegerField(blank=True, default=0)

    def __str__(self):
        if self.title is not None or self.title != '':
            text = self.title
        else:
            text=  self.text[0:20]

        return f'{self.article.game.name} sur {self.article.game.system.title}: {text}'

    def save(self, *args, **kwargs):
        self.id_num = len(self.article.inserts.all())+1
        super(Insert, self).save(*args, **kwargs)

    class Meta:
        # ordering = ['article__game__name']
        verbose_name = 'Gestion de l\encart'
        verbose_name_plural = 'Gestion des encarts'


class Opinion(models.Model):
    article = models.ForeignKey(Article, related_name='opinions', on_delete=models.CASCADE)
    text = models.TextField(max_length=1500)
    tester = models.CharField(max_length=35)
    advice = models.CharField(max_length=25, blank=True)
    id_num = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.tester} - {self.text[0:40]}'

    def save(self, *args, **kwargs):
        self.id_num = len(self.article.opinions.all())+1
        super(Opinion, self).save(*args, **kwargs)

    class Meta:
        # ordering = ['article__game__name']
        verbose_name = 'Gestion de l\'avis testeur'
        verbose_name_plural = 'Gestion des avis testeurs'


class Score(models.Model):
    article = models.ForeignKey(Article, related_name='scores', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    score = models.CharField(max_length=15)
    text = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f'{self.article.game.name} sur {self.article.game.system.title}: {self.title} {self.score}'

    class Meta:
        # ordering = ['article__game__name']
        verbose_name = 'Gestion des notes'
        verbose_name_plural = 'Gestion des notes'


class Photo(models.Model):
    link = models.SlugField(max_length=100, null=False, blank=True)
    text = models.TextField(max_length=500)
    id_num = models.IntegerField(blank=True, default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.id_num} - {self.link}'


class PhotoArticle(Photo):
    article = models.ForeignKey(Article, related_name='photos',on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        num = len(self.article.photos.all()) + 1
        self.id_num = num
        # link = f'{self.article.game.name} {self.article.title_mag} {self.article.num_mag}_{num}'
        # self.link = slugify(link)
        super(Photo, self).save(*args, **kwargs)

    class Meta:
        # ordering = ['article__game__name']
        verbose_name = 'Gestion de la photo de l\'article'
        verbose_name_plural = 'Gestion des photos des articles'


class PhotoInsert(Photo):
    insert = models.ForeignKey(Insert, related_name='photos', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        num = len(self.insert.photos.all()) + 1
        self.id_num = num
        link = f'encart {self.insert.id}_{num}'
        self.link = slugify(link)
        super(Photo, self).save(*args, **kwargs)

    class Meta:
        ordering = ['insert']
        verbose_name = 'Gestion de la photo de l\'encart'
        verbose_name_plural = 'Gestion des photos des encarts'


class Link(models.Model):
    article = models.ForeignKey(Article, related_name='links', on_delete=models.CASCADE)
    url = models.URLField(max_length=200)

    # def __str__(self):
    #     return f'{self.article.game.name} sur {self.article.game.system.title} [{self.url[0:50]}...{self.url[-50:]}]'

    class Meta:
        # ordering = ['article__game__name']
        verbose_name = 'Gestion du lien'
        verbose_name_plural = 'Gestion des liens'


class Paragraph(models.Model):
    article = models.ForeignKey(Article, related_name='paragraphs', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100, blank=True)
    text = models.TextField(max_length=2500)
    id_num = models.IntegerField(blank=True, default=0)

    # def __str__(self):
    #     return f'{self.id_num}: {self.article.game} - {self.text[0:100]}'

    def save(self, *args, **kwargs):
        self.id_num = len(self.article.paragraphs.all())+1
        super(Paragraph, self).save(*args, **kwargs)

    class Meta:
        # ordering = ['article__game__name']
        verbose_name = 'Gestion du paragraphe'
        verbose_name_plural = 'Gestion des paragraphes'
