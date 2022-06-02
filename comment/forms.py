from django import forms
from comment.models import Comment

class CommentForm(forms.ModelForm):
	comment_id = forms.IntegerField(widget=forms.HiddenInput())

	class Meta:
		model = Comment
		exclude = ('created_at', 'article',
			'author', 'like_count', 'dislike_count') 

		widgets = {
			'content': forms.Textarea(attrs={
				'class': 'form-control',
				'cols': 80,
				'rows': 5})
		}

		labels = {
           'content' : '',
        }
