from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from game.models import Game, System
from django.conf import settings
from slugify import slugify
import configparser
from time import gmtime, strftime
import re

class My_Article:
    def __init__(self, config):
        self.code = config['info']['id']
        self.type = config['info']['type']
        self.template = config['article']['template']
        self.article_type = config['article']['type']
        self.article_preface = config['article']['preface']
        self.link_mag = config['magazine']['link']
        self.mag = config['magazine']['title']
        self.num = config['magazine']['numero']
        self.site = config['magazine']['site']
        self.paragraphes = config['paragraphes']
        self.photos = config['photos']
        self.notes = config['notes']
        self.link_photo = config['prop']['link_image']
        self.links = config['article']['links']
        self.encarts = config['encarts']
        self.moins = config['moins']
        self.plus = config['plus']

        if config['info']['type'] == 'game':
            self.title = config['jeux']['title']
            self.support = config['jeux']['support']
            self.id_sc = config['jeux']['id_sc']

    def create_title(self):
        context = {
            'article_type': self.article_type,
            'title': self.title,
            'support': self.support.upper(),
            'mag': self.mag,
            'num': self.num,
            }

        return render_to_string('magazine/partial/template_title.html', context)

    def create_preface(self):
        context = {
            "preface": self.article_preface}

        return render_to_string("magazine/partial/template_preface.html", context)

    def create_paragraphe(self, tab_paragraphe):

        num_paragraphe = tab_paragraphe[1]
        text = self.change_text(self.paragraphes[num_paragraphe])
        line = text.split(":::")
        title = None
        if len(line) > 1:
            title = line[0]
            text = line[1]
        else:
            text = line[0]

        context = {
            "title": title, "text": text}
        context['class'] = self.create_class(tab_paragraphe[0])

        return render_to_string("magazine/partial/template_paragraphe.html", context)

    def create_photo(self, tab_photo, mode=["photo"]):
        num_photo = tab_photo[0]
        alt = f"{self.title}_photo{num_photo}"
        text =""
        context = {'class': None}

        if mode[0] == "photo":
            text = self.photos[num_photo]
            link = f"{self.link_photo}/{self.mag}_{self.num}_{self.id_sc}/{num_photo}.avif"
            context['class'] = self.create_class(tab_photo[1])
        elif mode[0] == "encart":
            context['class'] = mode[2]['case']
            num = mode[1]
            link = f"{self.link_photo}/{self.mag}_{self.num}_{self.id_sc}/encart-{num}_{num_photo}.avif"

        context["text"] = text
        context["link"] = link
        context["alt"] = alt

        return render_to_string("magazine/partial/template_photo.html", context)

    def create_(self, num):
        case_photo = round(12/num)
        return f'col-md-{case_photo}'

    def create_encart(self, encart):
        num = encart[1]
        text = self.change_text(self.encarts[num])
        context = {}

        if "type=" in encart[0]:
            type_vue = re.findall("type=([a-z0-9-]{1,})", encart[0])[0]
            context["type"] = type_vue

        line = text.split(":::")
        indice_text = len(line) - 1
        if len(line) > 1:
            context['title'] = line[0]

        text = line[indice_text].split("\n")
        context['text'] = text[0]
        photos = text[1:]
        context['photos'] = []
        context['id'] = f'encart{num}'
        context['class'] = self.create_class(encart[0], "encart")

        i = 1
        num_photo = len(photos)
        my_class = self.create_class(num_photo, "photo")

        for photo in photos:
            context['photos'].append(self.create_photo([i], mode=["encart", num, {'case': my_class}]))
            i = i + 1

        return render_to_string("magazine/partial/template_encart.html", context)

    def create_note(self, note):
        context = {'notes': []}
        for field in self.notes:
            result = {'field': field}
            score = self.notes[field].split(":::")
            result['score'] = score[0]
            result['avis'] = None

            if len(score) > 1:
                result['avis'] = score[1]
            context['notes'].append(result)
        context['class'] = self.create_class(note)

        return render_to_string("magazine/partial/template_note.html", context)

    def create_note_pm(self, note):
        context = {
            'moins': self.moins, 'plus': self.plus, 'type': 'plus-moins'}
        context['class'] = self.create_class(note)

        return render_to_string("magazine/partial/template_note.html", context)

    def create_link(self):
        context = {}
        if self.type == 'game':
            context['link_mag'] = self.link_mag
            context['title_mag'] = f'{self.mag} numero {self.num}'
            context['title_site'] = self.site
            context['links'] = self.links.split(":::")

        return render_to_string("magazine/partial/template_link.html", context)

    def create_class(self, my_string, mode="auto"):
        result = ''
        x =None

        if mode in ['encart']:
            result = result + f" article_encart"

        if mode == "photo":
            mode = "case"
            if my_string > 0:
                case_photo = round(12/my_string)
                x = [[mode, case_photo]]
        else:
            x = re.findall(r"(case|offset)=([\d]+)", my_string)

        if x is not None:
            for i in x:
                if 'case' in i:
                    result = result + f" col-md-{i[1]}"
                elif 'offset' in i and int(i[1]) > 0:
                    result = result + f" offset-md-{i[1]}"
        
        return result.strip()

    def change_text(self, text):
        regex = {
            'bbcode': "\[([a-z]+)\]([\w\W]+)\[/([a-z]+)\]",
            'title_markdown': "(\*{2,6})([\w\W][^*]{2,6})+(\*{2,6})"}

        if re.search(regex['bbcode'], text):
            txts = re.findall(regex['bbcode'], text)
            for txt in txts:
                if txt[0] == 'signature':
                    replace_by = f'<span class="article_signature">{txt[1]}</span>'
                pattern = f"\[([a-z]+)\]{txt[1]}\[/([a-z]+)\]"
                text = re.sub(pattern, replace_by, text)

        if re.search(regex['title_markdown'], text):
            txts = re.findall(regex['title_markdown'], text)
            for txt in txts:
                if "*" in txt[0]:
                    pattern = "(\*{2,6})"+str(txt[1])+"(\*{2,6})"
                    replace_by = f'<h{len(txt[0])+1}>{txt[1]}</h{len(txt[0])+1}>'
                    text = re.sub(pattern, replace_by, text)
        return text

    def save(self, class_article):
        if self.type == "game":
            # self.create_game()
            slug = slugify(f"{self.title} {self.support} {self.mag} {self.num}")

        elif self.type == "musique":
            band = self.config['album']['band']
            title = self.config['album']['title']
            year =  self.config['album']['year']
            title_site = self.config['article']['site']
            title_mag = title_site
            num_mag= "0"
            chroniqueur = self.config['article']['chroniqueur']
            preface = self.config['paragraphes']['1']

            slug = slugify(f"{band} {title} {year} {title_site} {chroniqueur}")

        try:
            self.article = class_article.objects.get(slug=slug)
        except ObjectDoesNotExist:
            self.article = class_article(
                title=self.title,
                slug=slug,
                preface=self.article_preface,
                title_mag=self.mag,
                num_mag=self.num,
                my_id=self.code)
            self.article.save()

class Template:
    def __init__(self, name, models):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(f'{settings.PATH_LOCAL}magazine/articles/{name}.ini')
        self.article = My_Article(self.config)
        self.article.save(models)

    def return_template(self):
        regex = {
            'game.title': r"(@--\s?game.title[\w\s=]+--@)",
            'album.title': r"(@--\s?album.title[\w\s=]+--@)",
            'game.notes.pm': r"@-- game.notes.pm[\w\s=]+--@",
            'game.note': r"@-- game.notes[\w\s=]+--@",
            'album.tacklist': r"(@--\s?album.tacklist[\w\s=]+--@)",
            'paragraphe': r"(@--\s?paragraphe=(\d+) ([\w\s=]+)?--@)",
            'encart': r"(@--\s?encart=([0-9]{1,2})([\w\s=]+)?(type=([\w\s=-]+))?\s?--@)",
            'preface': r"@-- preface[\w\s=]+--@",
            'photo': r"@-- photo=(\d+) ([\w\s=]+)?--@",
            'add_link': r"@-- add_link[\w\s=]+--@",
        }

        if re.search(regex['game.title'], self.article.template):
            self.article.template = re.sub(regex['game.title'], self.article.create_title(), self.article.template)

        if re.search(regex['preface'], self.article.template):
            self.article.template = re.sub(regex['preface'], self.article.create_preface(), self.article.template)

        if re.search(regex['paragraphe'], self.article.template):
            paragraphes = re.findall(regex['paragraphe'], self.article.template)
            for paragraphe in paragraphes:
                pattern = f"@-- paragraphe={paragraphe[1]} ([\w\s=]+)?--@"
                self.article.template = re.sub(pattern, self.article.create_paragraphe(paragraphe), self.article.template)

        if re.search(regex['photo'], self.article.template):
            photos = re.findall(regex['photo'], self.article.template)
            for photo in photos:
                pattern = f"@-- photo={photo[0]} ([\w\s=]+)?--@"
                self.article.template = re.sub(pattern, self.article.create_photo(photo), self.article.template)

        if re.search(regex['add_link'], self.article.template):
            self.article.template = re.sub(regex['add_link'], self.article.create_link(), self.article.template)

        if re.search(regex['encart'], self.article.template):
            encarts = re.findall(regex['encart'], self.article.template)
            for encart in encarts:
                pattern = f"@--\s?encart={encart[1]}([\w\s=]+)?(type=([\w\s=-]+))?\s?--@"
                self.article.template = re.sub(pattern, self.article.create_encart(encart), self.article.template)

        if re.search(regex['game.note'], self.article.template):
            note = re.findall(regex['game.note'], self.article.template)[0]
            self.article.template = re.sub(regex['game.note'], self.article.create_note(note), self.article.template)

        if re.search(regex['game.notes.pm'], self.article.template):
            note = re.findall(regex['game.notes.pm'], self.article.template)[0]
            self.article.template = re.sub(regex['game.notes.pm'], self.article.create_note_pm(note), self.article.template)

# class Template:
#     def __init__(self, name):
#         self.config = configparser.ConfigParser(interpolation=None)
#         self.config.read(f'{settings.PATH_LOCAL}magazine/articles/{name}.ini')
#         self.article = Article(self.config)
#         self.template = self.config['article']['template']
#         self.info_type = self.config['info']['type']

#     def create_title(self, my_type="html"):
#         if self.info_type == 'musique':
#             return self.create_title_album(my_type)
#         elif self.info_type == 'game':
#             return self.create_title_article(my_type)

#     def create_title_album(self, my_type="html"):
#         band = self.config['album']['band']
#         title = self.config['album']['title']
#         year =  self.config['album']['year']
#         pk = self.config['info']['id']

#         title_site = self.config['article']['site']
#         url_site = self.config['article']['url']
#         chroniqueur = self.config['article']['chroniqueur']
#         url_article = self.config['article']['link']

#         link = f"<a href=\"{url_site}\">{title_site}</a>"
#         link_2 = f"<a href=\"{url_article}\">{chroniqueur}</a>"

#         if my_type == "html":
#             return f"""
#                 <div class="row">
#                     <div class="col-md-8">
#                         <h1>{band} - {title} [{year}]</h1>
#                         <h3>sur {link} écrit par {link_2}</h3>
#                     </div>
#                     <div class="col-md-4">
#                         <img  class="img-fluid" src="http://vianneyba.fr/images/cover/{pk}.avif">
#                     </div>
#                 </div>
#                 """
#         else:
#             return f"{band} - {title} [{year}] sur {title_site} écrit par {chroniqueur}"

#     def create_title_article(self, my_type="html"):
#         type_article = self.config['article']['type']
#         game_title = self.config['jeux']['title']
#         support = self.config['jeux']['support']
#         numero_mag = self.config['magazine']['numero']
#         title_mag = self.config['magazine']['title']

#         if my_type == "html":
#             if self.config['article']['type'] == "dossier":
#                 txt = f"<h1>{type_article.capitalize()}: {game_title}</h1>"
#             else:
#                 txt = f"<h1>{type_article.capitalize()} de {game_title}"

#             if support != "None":
#                 txt += f" sur {support.upper()}</h1>"
#             else:
#                 txt += f"</h1>"

#             txt += f"<h3>Dans le numéro {numero_mag} de {title_mag}</h3>"
#         else:
#             txt = f"{type_article.capitalize()} de {game_title} {support.capitalize()}"
#             txt += f" dans le numéro {numero_mag} de {title_mag}"

#         return txt

#     def search_el(self, my_string, genre=None, my_id=None, case=None):
#         x = re.findall(r"(case|offset)=([\d]+)", my_string)

#         if genre is not None and my_id is not None:
#             html_id = f" id=\"{genre}_{my_id}\""
#         elif genre is not None:
#             html_id = f" id=\"{genre}\""
#         else:
#             html_id =""

#         my = []
#         if genre == "avis":
#             my.append(f"article_avis")
#         if genre == "encart":
#             my.append(f"article_encart")

#         if case is not None:
#             my.append(f"col-md-{case}")
#         for i in x:
#             if 'case' in i:
#                 my.append(f"col-md-{i[1]}")
#             elif 'offset' in i and int(i[1]) > 0:
#                 my.append(f"offset-md-{i[1]}")

#         if len(my) != 0:
#             txt = f"<div{html_id} class=\"{' '.join(my)}\">\n"
#         else:
#             txt = f"<div{html_id}>\n"

#         return txt

#     def create_paragraphe(self, txt):
#         p = txt.split(":::")
#         title = None
#         if len(p) > 1:
#             title = p[0]
#             txt = p[1]
#         else:
#             txt = p[0]

#         paragraphe = ""
#         if title is not None:
#             paragraphe += f"\t<h1>{title}</h1>\n"
#         paragraphe += f"\t<p>{txt}</p>\n"

#         return paragraphe

#     def create_encart(self, my_id):
#         paragraphe = self.config['encarts'][my_id]
#         txt = ""
#         p = paragraphe.split(":::")
#         s = p[1].split("\n")
#         if p[0] != "none":
#             title = p[0]
#             txt += f"\t\t\t<h1>{title}</h1>"

#         text = s[0]
#         photos = s[1:]

#         txt += f"\t\t\t<p>{text}</p>"

#         txt += "<div class=\"row\">"
#         i = 1
#         case_photo = round(12/len(photos))
#         for photo in photos:
#             txt += f"<div class=\"col-md-{case_photo}\">"
#             link = self.config['magazine']['title']+"_"+self.config['magazine']['numero']+"_"+self.config['jeux']['id_sc']
#             link += f"/encart-{my_id}_{i}.avif"
#             txt += self.create_photo(i, text=photo, name=link)
#             txt += "</div>"
#             i += 1
#         txt += "</div>"

#         return txt

#     def create_avis(self, txt):
#         p = txt.split(":::")
#         tester = None
#         avis = None

#         if len(p) == 1:
#             txt = p[0]

#         elif len(p) == 2:
#             tester =  p[0]
#             txt = p[1]
#         elif len(p) == 3:
#             tester =  p[0]
#             avis = p[1]
#             txt = p[2]

#         my_div = f"\t<h1>Avis"
#         if tester is not None:
#             my_div += f" de <span class=\"avis_tester\">{tester}</span>"
#         if avis is not None:
#             my_div += f" <span class=\"avis_advice\">{avis}</span>"
#         my_div += "</h1>\n"
#         my_div += f"\t<p>{txt}</p>\n"

#         return my_div

#     def create_photo(self, my_id, text=None, name=None):
#         link = self.config['prop']['link_image']
#         if text == None:
#             photo = self.config['photos'][my_id]
#             link += "/"+self.config['magazine']['title']+"_"+self.config['magazine']['numero']+"_"+self.config['jeux']['id_sc']
#             link += f"/{my_id}.avif"
#         else:
#             photo = text
#             link += f"/{name}"

#         if text == "photo":
#             photo = ''

#         return f"""
#             <figure class="figure">
#                 <img
#                     class="figure-img img-fluid rounded"
#                     src="{link}"
#                     alt="{photo.replace('"', "'")}"
#                 />
#                 <figcaption>{photo}</figcaption>
#             </figure>
#         """

#     def create_preface(self):
#         i = re.findall(r"(@-- preface[\w\s=]+--@)", self.template)
#         my_div = self.search_el(i[0], genre="preface")
#         my_div += f"\t<p>{self.config['article']['preface']}</p>\n"
#         my_div += "</div>\n"

#         pattern = f"@-- preface[\w\s=]+--@"
#         self.template = re.sub(pattern, my_div, self.template)

#     def create_plus_moins(self):
#         table = "\t<table class=\"table score_table\">\n"
#         table +=  "\t\t<tr class=\"tr_master\">\n"
#         table += f"\t\t\t<th>Les Plus</th>\n"
#         table += f"\t\t</tr>\n"
#         for key, value in self.config.items('plus'):
#             table +=  "\t\t<tr class=\"tr_master\">\n"
#             table += f"\t\t\t<td class=\"article_plus\">{value}</td>\n"
#             table += f"\t\t</tr>\n"
#         table +=  "\t\t<tr class=\"tr_master\">\n"
#         table += f"\t\t\t<th>Les Moins</th>\n"
#         table += f"\t\t</tr>\n"
#         for key, value in self.config.items('moins'):
#             table +=  "\t\t<tr class=\"tr_master\">\n"
#             table += f"\t\t\t<td class=\"article_moins\">{value}</td>\n"
#             table += f"\t\t</tr>\n"

#         table += "\t</table>\n"

#         return table

#     def create_note(self):
#         table = "\t<table class=\"table score_table\">\n"
#         for key, value in self.config.items('notes'):
#             score = value.split(":::")
#             note = score[0].replace('/100', '%')
#             avis = None
#             if len(score) > 1:
#                 avis = score[1]

#             table +=  "\t\t<tr class=\"tr_master\">\n"
#             table += f"\t\t\t<td>{key.capitalize()}</td>\n"
#             table += f"\t\t\t<td class=\"artlice_score\">{note}</td>\n"
#             table += f"\t\t</tr>\n"
#             if avis is not None:
#                 table += f"\t\t<tr>\n"
#                 table +=f"\t\t\t<td colspan=\"2\">{avis}</td>\n"
#                 table += f"\t\t</tr>\n"

#         table += "\t</table>\n"

#         return table

#     def create_link(self, text=""):
#         my_div = self.search_el(text, case=12)
#         if self.info_type == 'game':
#             my_div += f"\t<a href=\"{self.config['magazine']['link']}\">{self.config['magazine']['title']} numero {self.config['magazine']['numero']}</a>"
#             my_div += " sur <a href=\"https://www.abandonware-magazines.org/index.php\">Abandonware Magazines</a> >> "

#             links = self.config['article']['links'].split(":::")

#             i = 1
#             for link in links:
#                 my_div += f"<a href=\"{link}\">page {i}</a>\n"

#                 if i != len(links):
#                     my_div += " | "
#                 i += 1


#         my_div += "</div>\n"
#         return my_div

#     def _create_link(self):
#         i = re.findall(r"(@-- add_link[\w\s=]+--@)", self.template)
#         my_div = self.create_link(i[0])

#         pattern = f"@-- add_link[\w\s=]+--@"
#         self.template = re.sub(pattern, my_div, self.template)

#     def create_my_div(self, regex, txt):
#         i = re.findall(regex, self.template)
#         my_div = self.search_el(i[0])
#         my_div += f"\t{txt}\n"
#         my_div += "</div>"
#         self.template = re.sub(regex, my_div, self.template)

#     def create_tacklist(self):
#         txt = "\t<div class=\"article_tracklist\">\n"
#         txt += "\t\t<h5>Tracklist</h5>\n"
#         txt += "\t\t<ul class=\"list-group\">\n"
#         for key, track in self.config.items('tracklist'):
#             txt += f"\t\t\t<li class=\"list-group-item list-group-item-dark\">{key}. {track}</li>\n"
#         txt += "\t\t</ul>\n"
#         txt += "\t</div>\n"

#         return txt

#     def return_template(self):
#         regex = {
#             'game.title': r"(@--\s?game.title[\w\s=]+--@)",
#             'album.title': r"(@--\s?album.title[\w\s=]+--@)",
#             'game.notes.pm': r"(@--\s?game.notes.pm[\w\s=]+--@)",
#             'album.tacklist': r"(@--\s?album.tacklist[\w\s=]+--@)",
#             'paragraphe': r"(@--\s?paragraphe=(\d+) ([\w\s=]+)?--@)",
#             'encart': r"(@--\s?encart=([0-9]{1,2})([\w\s=]+)?--@)"
#         }
#         if re.search(regex['game.title'], self.template):
#             txt = self.create_title_article(my_type='html')
#             self.create_my_div(regex['game.title'], txt)

#         if re.search(regex['album.title'], self.template):
#             txt = self.create_title_album()
#             self.create_my_div(regex['album.title'], txt)

#         if re.search(regex['album.tacklist'], self.template):
#             txt = self.create_tacklist()
#             self.create_my_div(regex['album.tacklist'], txt)

#         if re.search(regex['paragraphe'], self.template):
#             i = re.findall(regex['paragraphe'], self.template)
#             for paragraphe in i:
#                 my_div = self.search_el(paragraphe[0], genre="paragraphe", my_id=paragraphe[1])
#                 my_div += self.create_paragraphe(self.config['paragraphes'][paragraphe[1]])
#                 my_div += "</div>"
#                 pattern = f"@-- paragraphe={paragraphe[1]} ([\w\s=]+)?--@"
#                 self.template = re.sub(pattern, my_div, self.template)

#         if re.search(regex['game.notes.pm'], self.template):
#             txt = self.create_note()
#             txt += self.create_plus_moins()
#             self.create_my_div(regex['game.notes.pm'], txt)

#         if re.search(r"@-- avis=(\d+)[\w\s=]+--@", self.template):
#             i = re.findall(r"(@-- avis=(\d+)[\w\s=]+--@)", self.template)
#             for avis in i:
#                 my_div = self.search_el(avis[0], genre="avis", my_id=avis[1])
#                 my_div += self.create_avis(self.config['avis'][avis[1]])
#                 my_div += "</div>"
#                 pattern = f"@-- avis={avis[1]}[\w\s=]+--@"
#                 self.template = re.sub(pattern, my_div, self.template)

#         if re.search(r"@-- game.notes[\w\s=]+--@", self.template):
#             i = re.findall(r"(@-- game.notes[\w\s=]+--@)", self.template)
#             my_div = self.search_el(i[0], genre="notes")
#             my_div += self.create_note()
#             my_div += "</div>"
#             pattern = f"@-- game.notes[\w\s=]+--@"
#             self.template = re.sub(pattern, my_div, self.template)

#         if re.search(r"@-- photo=(\d+)[\w\s=]+--@", self.template):
#             i = re.findall(r"(@-- photo=(\d+)[\w\s=]+--@)", self.template)
#             for photo in i:
#                 my_div = self.search_el(photo[0], genre="photo", my_id=photo[1])
#                 my_div += self.create_photo(photo[1])
#                 my_div += "</div>"
#                 pattern = f"@-- photo={photo[1]}[\w\s=]+--@"
#                 self.template = re.sub(pattern, my_div, self.template)

#         if re.search(regex['encart'], self.template):
#             i = re.findall(regex['encart'], self.template)
#             for encart in i:
#                 my_div = self.search_el(encart[0], genre="encart", my_id=encart[1])
#                 my_div += self.create_encart(encart[1])
#                 my_div += "</div>"
#                 pattern = f"@-- encart={encart[1]}[\w\s=]+--@"
#                 self.template = re.sub(pattern, my_div, self.template)

#         if re.search(r"@-- preface[\w\s=]+--@", self.template):
#             self.create_preface()

#         if re.search(r"@-- add_link[\w\s=]+--@", self.template):
#             self._create_link()

#         return ''.join(('<article>',self.template,'\n</article>'))

#     def export_pelican(self):
#         title = self.create_title_article(my_type="md")
#         tags = self.config['jeux']['tags'].replace(":::", ", ")
#         category = self.config['article']['category']
#         txt = self.return_template()

#         return f"""
#         <html>
#             <head>
#                 <title>{title}</title>
#                 <meta name="tags" content="{tags}" />
#                 <meta name="date" content="{strftime("%Y-%m-%d %H:%M", gmtime())}" />
#                 <meta name="category" content="{category}" />
#                 <meta name="authors" content="VianneyBa" />
#             </head>

#             <body>
#                 {txt}
#             </body>
#         </html>
#         """

class Export:
    def __init__(self, class_article):
        self.class_article = class_article
        self.config = configparser.ConfigParser(interpolation=None)
        self.url = f"{settings.PATH_LOCAL}magazine/articles/"

    def save_ini(self):
        with open(f"{self.url}{self.config['info']['id']}.ini", "w") as configfile:
            self.config.write(configfile)

    def create_ini(self, txt):
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        name = ''.join(secrets.choice(alphabet) for i in range(12))
        self.write_file(name, txt)


        self.config.read(f"{settings.PATH_LOCAL}{self.url}{name}.ini")
        self.config['info']['id'] = name
        self.save_ini()

        if self.config['article']['category'] == "jeux vidéo":
            self.create_game()
            self.create_article(my_type="game")
        elif self.config['article']['category'] == "musique":
            self.create_article(my_type="musique")
        

    def write_file(self, name, txt):
        file = open(f"{self.url}{name}.ini","w")
        file.write(txt)
        file.close()
        self.read_file(name)
        
    def read_file(self, name):
        self.config.read(f'magazine/articles/{name}.ini')

    def create_article(self, my_type=None):
        my_type = self.config['info']['type']
# {% A FAIRE %}
        if my_type == "game":
            self.create_game()
            title = self.config['jeux']['title']
            title_article = title
            support = self.config['jeux']['support']
            title_mag = self.config['magazine']['title']
            num_mag = self.config['magazine']['numero']
            preface = self.config['article']['preface']
            slug = slugify(f"{title} {support} {title_mag} {num_mag}")

        elif my_type == "musique":
            band = self.config['album']['band']
            title = self.config['album']['title']
            year =  self.config['album']['year']
            title_site = self.config['article']['site']
            title_mag = title_site
            num_mag= "0"
            chroniqueur = self.config['article']['chroniqueur']
            preface = self.config['paragraphes']['1']

            slug = slugify(f"{band} {title} {year} {title_site} {chroniqueur}")

        try:
            self.article = self.class_article.objects.get(slug=slug)
        except ObjectDoesNotExist:
            self.article = self.class_article(
                title=title,
                slug=slug,
                preface=preface,
                title_mag=title_mag,
                num_mag=num_mag,
                my_id=self.config['info']['id'])
            self.article.save()

    def create_game(self):
        search_game = self.config['jeux']['title']
        search_system = self.create_system()
        try:
            self.game = Game.objects.get(name=search_game, system=search_system)
        except ObjectDoesNotExist:
            self.game = Game(
                name=self.config['jeux']['title'],
                sc_id=self.config['jeux']['id_sc'],
                system=self.create_system()
            ).save()

    def create_system(self):
        search = self.config['jeux']['support']
        try:
            system = System.objects.get(slug=search)
        except ObjectDoesNotExist:
            system = System(
                title=search,
                slug=search).save()
        
        return system
