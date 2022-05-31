from django import forms

class CommentForm(forms.Form):
	comment_content = forms.CharField(
		label='Votre commentaire',
		widget=forms.Textarea(attrs={'class': 'form-control'}))
	article_id = forms.CharField(widget=forms.HiddenInput())