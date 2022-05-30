from django import forms

class loginForm(forms.Form):
	username= forms.CharField(label='Your name', max_length=100)
	password= forms.CharField(label='password', max_length=100)