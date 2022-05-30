from django import forms

class CommentForm(forms.Form):
	comment = forms.CharField(
		label='Votre commentaire',
		widget=forms.Textarea(attrs={'class': 'form-control'}))