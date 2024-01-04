from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify
from magazine.models import Article
from magazine.forms import ArticleForm, ParagraphForm, PhotoForm, InsertForm, LinkForm, ScoreForm


def write_article(request):
    form_write_article = ArticleForm()
    if request.method == 'POST':
        form_write_article = ArticleForm(request.POST)
        if form_write_article.is_valid():
            article = form_write_article.save(commit=False)
            link = f'{article.game.name} {article.title_mag} {article.num_mag}'
            article.slug = slugify(link)
            article.save()
            return redirect('magazine:view-article', pk=article.id)

    context = {'form_write_article': form_write_article}
    return render(request, 'magazine/write-article.html', context)


def add_paragraph(request, pk):
    article = Article.objects.get(id=pk)
    form_add_paragraph = ParagraphForm(initial={'article': article.id})

    if request.method == 'POST':
        form_add_paragraph = ParagraphForm(request.POST)
        if form_add_paragraph.is_valid():
            form_add_paragraph.save()
            return redirect('magazine:add-paragraph', pk=article.id)

    context = {'form_add_paragraph': form_add_paragraph, 'article': article}
    return render(request, 'magazine/add-paragraph.html', context)


def add_photo(request, pk):
    article = Article.objects.get(id=pk)
    form = PhotoForm(initial={'article': article.id})

    if request.method == 'POST':
        form = PhotoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:add-photo', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-photo.html', context)


def add_insert(request, pk):
    article = Article.objects.get(id=pk)
    form = InsertForm(initial={'article': article.id})

    if request.method == 'POST':
        form = InsertForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:add-insert', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-insert.html', context)


def add_link(request, pk):
    article = Article.objects.get(id=pk)
    form = LinkForm(initial={'article': article.id})

    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:add-link', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-link.html', context)


def add_score(request, pk):
    article = Article.objects.get(id=pk)
    form = ScoreForm(initial={'article': article.id})

    if request.method == 'POST':
        form = ScoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('magazine:add-score', pk=article.id)

    context = {'form': form, 'article': article}
    return render(request, 'magazine/add-score.html', context)

def view_article(request, pk):
    article = Article.objects.get(id=pk)
    context = {'article': article}

    print(article.paragraph_set.all())
    return render(request, 'magazine/view-article.html', context)
