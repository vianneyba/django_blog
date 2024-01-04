from django import forms
from magazine.models import Article, Paragraph, PhotoArticle, Insert, Link, Score

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'


class ParagraphForm(forms.ModelForm):
    class Meta:
        model = Paragraph
        fields = '__all__'


class PhotoForm(forms.ModelForm):
    class Meta:
        model = PhotoArticle
        fields = '__all__'


class InsertForm(forms.ModelForm):
    class Meta:
        model = Insert
        fields = '__all__'


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = '__all__'
        

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = '__all__'