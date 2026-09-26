from django import forms
from comment.models import Comment

class CommentForm(forms.ModelForm):
    comment_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "auth-input",
                "rows": 5,
                "placeholder": "Ton commentaire…",
            })
        }
        labels = {"content": ""}