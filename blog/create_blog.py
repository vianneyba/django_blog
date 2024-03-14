import re
import markdown
from django.urls import reverse
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from game.models import Game
from polls.models import Title_Suggestion, Liste_Title, Choice_Liste_Title
from magazine.convert_ini import Template

class Blog_Article:
    patterns = {
        "p_add_form_title_suggestion": r"{{ add_form_title_suggestion sc_id=([0-9]{1,}) }}",
        "p_top_list": r"{{ top_list slug=([0-9-a-z-]{1,}) }}",
        "p_article": r"{{ article=([0-9a-zA-Z-]{1,}) }}",
        "choice_type": r"{{ type=(markdown|html) }}",
    }

    def __init__(self, blog, request):
        self.crfs = get_token(request)
        self.request = request
        self.blog = blog

        if re.search(self.patterns['p_add_form_title_suggestion'], self.blog.content):
            self.add_title_suggestion()
        if re.search(r"{{ top_list slug=([0-9-a-z-]{1,}) }}", self.blog.content):
            self.add_top_list()
        if re.search(self.patterns['p_article'], self.blog.content):
            self.add_article()
        if re.search(self.patterns['choice_type'], self.blog.content):
            self.choice_type()

    def add_title_suggestion(self):
        """
            Ajout d'un formulaire pour rentrer un titre qui serait proche de notre jeux
        """

        # recherche de l'id du jeu
        x = re.search(self.patterns['p_add_form_title_suggestion'], self.blog.content)
        sc_id = x.groups()[0]

        # récupération du jeux
        game = Game.objects.get(sc_id=sc_id)

        suggestion = None
        if self.request.GET.get('suggestion'):
            suggestion = Title_Suggestion.objects.get(pk=self.request.GET.get('suggestion'))

        url = reverse("polls:add-title-suggestion")
        content = render_to_string("polls/form_title_suggestion.html", {
            'user': self.request.user,
            'article_blog': self.blog,
            'url': url,
            'csrf': self.crfs,
            'id': game.id,
            'suggestion': suggestion})

        self.blog.content = re.sub(self.patterns['p_add_form_title_suggestion'], content, self.blog.content)

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

    def add_article(self):
        x = re.search(self.patterns['p_article'], self.blog.content)
        slug = x.groups()[0]

        my_file = f"magazine.article.{slug}"

        template = Template(slug)
        self.blog.content = re.sub(self.patterns['p_article'], template.return_template(), self.blog.content)
    
    def choice_type(self):
        x = re.search(self.patterns['choice_type'], self.blog.content)
        my_type = x.groups()[0]
        print("x = "+x.groups()[0])
        if my_type == 'markdown':
            print("je suis du markdown")
            self.blog.content = markdown.markdown(self.blog.content)

        self.blog.content = re.sub(self.patterns['choice_type'], '', self.blog.content)