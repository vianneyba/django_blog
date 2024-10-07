import datetime
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db import models
from game.models import Game

# TYPE_CHOICES = [
#     ('test', 'test'), ('preview', 'preview')
# ]

class Title_Suggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    suggestion = models.CharField(max_length=200)

    def __str__(self):
        return(f'{self.user.username} sur {self.game.name} avec {self.suggestion}')

    class Meta:
        verbose_name = 'Gestion Des Jeux Identiques'
        verbose_name_plural = 'Gestion Des Jeux Identiques'


class Question(models.Model):
    # type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='test')
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("Date de publication")
    closing_date = models.DateTimeField("Date de cloture")


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)


class Liste_Title(models.Model):
    title = models.CharField(max_length=200)
    num_choice_max = models.IntegerField(default=1)
    slug = models.SlugField(unique=True, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True, blank=True)

    def save(self, *args, **kwargs):
        date = datetime.datetime.now()
        slug = f'{self.title} {date.day} {date.month} {date.year}'
        self.slug = slugify(slug)
        super(Liste_Title, self).save(*args, **kwargs)

    def create_counter(self):
        return range(1 ,self.num_choice_max+1)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Gestion Du Top'
        verbose_name_plural = 'Gestion Des Tops'


class Choice_Liste_Title(models.Model):
    liste = models.ForeignKey(Liste_Title, related_name='choices', on_delete=models.CASCADE, null=True)
    num_id = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    suggestion = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.liste}: {self.num_id} - {self.suggestion}'

    class Meta:
        verbose_name = 'Gestion Des Résultats Top'
        verbose_name_plural = 'Gestion Des Résultats Top'
