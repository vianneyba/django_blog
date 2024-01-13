from django import forms
from blog.models import Article as ArticleBlog

class ArticleForm(forms.ModelForm):
    class Meta:
        model = ArticleBlog
        exclude = ('created_at', 'published', 'update_date',
            'author', 'like_count', 'dislike_count', 'slug')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'cols': 80,
                'rows': 10,
                'placeholder': 'Description'}),
            'category': forms.Select(attrs={
                'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control'}),
            'banner': forms.TextInput(attrs={
                'class': 'form-control'}), 
            'articles_mag': forms.CheckboxSelectMultiple()
        }



