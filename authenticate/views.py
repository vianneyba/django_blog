from django.shortcuts import render, redirect
from .forms import loginForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout

def myLogout(request):
	logout(request)
	return redirect('blog:index')

def myLogin(request):
	if request.method == 'GET' and 'HTTP_REFERER' in request.META:
		request.session['last_page'] = request.META["HTTP_REFERER"]

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			if 'last_page' in request.session:
				return redirect(request.session['last_page'])
			else:
				return redirect('blog:index')
		else:
			errors = "il y a quelque chose qui ne va pas avec ce que vous avez entré!"
			return render(request, 'authenticate/login.html', {'form': loginForm, 'errors': errors})
		 
	return render(request, 'authenticate/login.html', {'form': loginForm})

def myregister(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)

		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			return redirect('blog:index')
	else:
		form = UserCreationForm()

	context = {'form': form}
	return render(request, 'authenticate/register.html', context)
