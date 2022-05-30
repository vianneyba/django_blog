from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from comment.forms import CommentForm
from comment.models import Comment
from blog.models import Article
from markdown import markdown

@login_required
def add(request, article_id):
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.cleaned_data['comment']
			user = request.user
			article = Article.objects.get(pk=article_id)
			newcomment = Comment(user= user, content= comment, article_id= article.id)
			newcomment.save()

			return redirect('blog:index')
	else:
		form= CommentForm()

	context= {'form': form, 'article_id': article_id}
	return render(request, 'comment/add.html', context)

def view(request):
	pass