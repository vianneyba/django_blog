from django import forms
from polls.models import Title_Suggestion


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Title_Suggestion
        fields = ['suggestion', 'game']
        widgets = {
            'suggestion': forms.TextInput(attrs={
                'class': 'form-control'}),
        }