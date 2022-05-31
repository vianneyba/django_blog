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
			context = return_article(request, id=request.POST['article_id'])
			form_comment = CommentForm()
			form_comment.fields["article_id"].initial = context['article'].id

			context['form_comment'] = form_comment
			return render(request, 'blog/view-article.html', context)

def view(request):
	pass