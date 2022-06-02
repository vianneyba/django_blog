from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from comment.forms import CommentForm
from comment.models import Comment
from blog.models import Article
from blog.views import return_article
from markdown import markdown

@login_required
def add(request, article_id):
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			content = form.cleaned_data['comment_content']
			article_id = form.cleaned_data['article_id']
			user = request.user
			article = Article.objects.get(pk=article_id)
			comment = Comment(user= user, content=content, article_id=article_id)
			comment.save()
			return redirect('blog:by-slug', slug=article.slug)
		else:
			context = return_article(request, pk=request.POST['article_id'])
			form_comment = CommentForm()
		
			context['form_comment'] = form_comment
			return render(request, 'blog/view-article.html', context)

@login_required
def update(request, article_id, comment_id):
	comment = Comment.objects.get(pk=comment_id)
	context = return_article(request, pk=article_id)

	if request.method == 'POST':
		form = CommentForm(request.POST, instance=comment)
		if form.is_valid():
			form.save()
			return redirect('blog:by-slug', slug=context['article'].slug)
			# return render(request, 'blog/view-article.html', context)

	form_comment = CommentForm(instance=comment)
	form_comment.fields["comment_id"].initial = comment.id

	context['form_comment'] = form_comment
	context['type'] = 'update'
	return render(request, 'blog/view-article.html', context)
