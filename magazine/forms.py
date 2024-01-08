from django import forms
from magazine import models

class ArticleForm(forms.ModelForm):
    class Meta:
        model = models.Article
        fields = '__all__'
        exclude = ('slug',)
        widgets = {
            'preface': forms.Textarea(attrs={
                'class': 'form-control',
                'cols': 80,
                'rows': 10}),
            'title_mag': forms.TextInput(attrs={
                'class': 'form-control'}),
            'num_mag' : forms.TextInput(attrs={
                'class': 'form-control'}),
        }


class ParagraphForm(forms.ModelForm):
    class Meta:
        model = models.Paragraph
        fields = '__all__'
        exclude = ('id_num',)


class PhotoForm(forms.ModelForm):
    class Meta:
        model = models.PhotoArticle
        fields = '__all__'
        exclude = ('id_num', 'link')


class PhotoInsertForm(forms.ModelForm):
    class Meta:
        model = models.PhotoInsert
        fields = '__all__'
        exclude = ('id_num', 'link')


class InsertForm(forms.ModelForm):
    class Meta:
        model = models.Insert
        fields = '__all__'
        exclude = ('id_num',)


class LinkForm(forms.ModelForm):
    class Meta:
        model = models.Link
        fields = '__all__'
        

class ScoreForm(forms.ModelForm):
    class Meta:
        model = models.Score
        fields = '__all__'

class OpinionForm(forms.ModelForm):
    class Meta:
        model= models.Opinion
        fields = '__all__'
        exclude = ('id_num',)
