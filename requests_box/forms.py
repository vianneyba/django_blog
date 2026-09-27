# requests_box/forms.py
from django import forms
from .models import SiteRequest

class SiteRequestForm(forms.ModelForm):
    class Meta:
        model = SiteRequest
        fields = ["kind", "name", "email", "username", "message"]
        widgets = {
            "kind": forms.Select(attrs={"class": "auth-input"}),
            "name": forms.TextInput(attrs={"class": "auth-input"}),
            "email": forms.EmailInput(attrs={"class": "auth-input"}),
            "username": forms.TextInput(attrs={"class": "auth-input"}),
            "message": forms.Textarea(attrs={"class": "auth-input", "rows": 5}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields["name"].initial = user.get_full_name() or user.username
            self.fields["email"].initial = user.email
            self.fields["username"].initial = user.username