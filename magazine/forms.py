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