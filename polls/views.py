from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from polls.forms import SuggestionForm
from polls.models import Liste_Title, Choice_Liste_Title

def add_title_suggestion(request):
    form = SuggestionForm()
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.user = request.user
            suggestion.save()

            url = reverse("blog:by-slug", args=(request.POST.get("article_blog"),))
            link = f'{url}?suggestion={suggestion.id}'
            return redirect(link)

    context = {'form': form}
    return render(request, 'polls/form_title_suggestion.html', context)


def valid_liste_title(request):
    if request.method == 'POST':
        top = Liste_Title.objects.get(id=request.POST.get('id_top'))
        d = request.POST.dict()

        for key, value in d.items():
            if key[0:7] == 'choice_':
                num_id = key[7:]
                try:
                    my_list = Choice_Liste_Title.objects.get(num_id=num_id, user=request.user)
                    my_list.suggestion = value
                except:
                    my_list = Choice_Liste_Title(liste=top, num_id=num_id, user=request.user, suggestion=value)
                my_list.save()

        url = reverse("blog:by-slug", args=(request.POST.get("article_blog"),))
        return redirect(url)
        
    return render(request, 'polls/form_title_suggestion.html')
        


        
        
