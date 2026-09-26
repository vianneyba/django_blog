from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from comment.forms import CommentForm
from comment.models import Comment
from blog.models import Article
from blog.views import return_article
from markdown import markdown

@login_required
def add(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.article = article
            comment.save()
            return redirect("blog:by-slug", slug=article.slug)

        context = return_article(request, pk=article_id)
        context["form_comment"] = form
        return render(request, "blog/view-article.html", context)

    return redirect("blog:by-slug", slug=article.slug)

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
