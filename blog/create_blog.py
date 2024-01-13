import re
from django.urls import reverse
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from game.models import Game
from polls.models import Title_Suggestion, Liste_Title, Choice_Liste_Title

class Blog_Article:
    def __init__(self, blog, request):
        self.crfs = get_token(request)
        self.request = request
        self.blog = blog

        if re.search(r"{{ add_form_title_suggestion sc_id=([0-9]{1,}) }}", self.blog.content):
            self.add_title_suggestion()
        if re.search(r"{{ top_list slug=([0-9-a-z-]{1,}) }}", self.blog.content):
            self.add_top_list()
        

    def add_title_suggestion(self):
        """
            Ajout d'un formulaire pour rentrer un titre qui serait proche de notre jeux
        """

        # recherche de l'id du jeu
        x = re.search(r"{{ add_form_title_suggestion sc_id=([0-9]{1,}) }}", self.blog.content)
        sc_id = x.groups()[0]

        # récupération du jeux
        game = Game.objects.get(sc_id=sc_id)

        suggestion = None
        if self.request.GET.get('suggestion'):
            suggestion = Title_Suggestion.objects.get(pk=self.request.GET.get('suggestion'))

        url = reverse("polls:add-title-suggestion")
        content = render_to_string("polls/form_title_suggestion.html", {
            'article_blog': self.blog,
            'url': url,
            'csrf': self.crfs,
            'id': game.id,
            'suggestion': suggestion})


        pattern = r"{{ add_form_title_suggestion sc_id=[0-9]{1,} }}"
        self.blog.content = re.sub(pattern, content, self.blog.content)

    def add_top_list(self):
        """"
            Ajout d'un Top
        """

        # recherche du slug du top
        x = re.search(r"{{ top_list slug=([0-9-a-z-]{1,}) }}", self.blog.content)
        slug = x.groups()[0]

        top = Liste_Title.objects.get(slug=slug)
        my_top = []

        if self.request.user.is_anonymous == False:
            my_top = Choice_Liste_Title.objects.filter(user=self.request.user, liste=top).order_by('num_id')

        if len(my_top) < top.num_choice_max:
            my_top = []
            for a in range(1,4):
                l = Choice_Liste_Title(suggestion='')
                my_top.append(l)

        url = reverse("polls:valid-top")
        content = render_to_string("polls/form_liste_title.html", {
            'user': self.request.user,
            'article_blog': self.blog,
            'top': top,
            'url': url,
            'csrf': self.crfs,
            'my_top': my_top})

        pattern = r"{{ top_list slug=([0-9-a-z-]{1,}) }}"
        self.blog.content = re.sub(pattern, content, self.blog.content)

