from django import forms
from vianneyba.context_processors import CATEGORIES
from blog.models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
      model = Article
      exclude = ('created_at', 'published', 'update_date',
        'author', 'like_count', 'dislike_count') 
    # title = forms.CharField(label='Titre: ', max_length=100)
    # content = forms.CharField(widget=forms.Textarea)
    # slug = forms.CharField(label='Slug: ', max_length=100, required=False)
    # category = forms.ChoiceField(
    #     widget=forms.Select,
    #     choices=CATEGORIES,
    # )
    # tags = forms.CharField(label='Tags: ', max_length=200)


