from django import forms
from blog.models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ('created_at', 'published', 'update_date',
            'author', 'like_count', 'dislike_count')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'}),
            'slug': forms.TextInput(attrs={
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
        }



