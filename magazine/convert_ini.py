from django.core.exceptions import ObjectDoesNotExist
from game.models import Game, System
from slugify import slugify
import configparser
from time import gmtime, strftime
import re

class Template:
    def __init__(self, name):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(f'magazine/articles/{name}.ini')
        self.template = self.config['article']['template']
        self.info_type = self.config['info']['type']

    def create_title(self, my_type="html"):
        if self.info_type == 'musique':
            return self.create_title_album(my_type)
        elif self.info_type == 'game':
            return self.create_title_article(my_type)

    def create_title_album(self, my_type="html"):
        band = self.config['album']['band']
        title = self.config['album']['title']
        year =  self.config['album']['year']
        pk = self.config['info']['id']

        title_site = self.config['article']['site']
        url_site = self.config['article']['url']
        chroniqueur = self.config['article']['chroniqueur']
        url_article = self.config['article']['link']

        link = f"<a href=\"{url_site}\">{title_site}</a>"
        link_2 = f"<a href=\"{url_article}\">{chroniqueur}</a>"

        if my_type == "html":
            return f"""
                <div class="row">
                    <div class="col-md-8">
                        <h1>{band} - {title} [{year}]</h1>
                        <h3>sur {link} écrit par {link_2}</h3>
                    </div>
                    <div class="col-md-4">
                        <img  class="img-fluid" src="http://vianneyba.fr/images/cover/{pk}.avif">
                    </div>
                </div>
                """
        else:
            return f"{band} - {title} [{year}] sur {title_site} écrit par {chroniqueur}"

    def create_title_article(self, my_type="html"):
        type_article = self.config['article']['type']
        game_title = self.config['jeux']['title']
        support = self.config['jeux']['support']
        numero_mag = self.config['magazine']['numero']
        title_mag = self.config['magazine']['title']

        if my_type == "html":
            if self.config['article']['type'] == "dossier":
                txt = f"<h1>{type_article.capitalize()}: {game_title}</h1>"
            else:
                txt = f"<h1>{type_article.capitalize()} de {game_title}"
                
            if support != "None":
                txt += f" sur {support.upper()}</h1>"
            else:
                txt += f"</h1>"

            txt += f"<h3>Dans le numéro {numero_mag} de {title_mag}</h3>"
        else:
            txt = f"{type_article.capitalize()} de {game_title} {support.capitalize()}"
            txt += f" dans le numéro {numero_mag} de {title_mag}"

        return txt

    def search_el(self, my_string, genre=None, my_id=None, case=None):
        x = re.findall(r"(case|offset)=([\d]+)", my_string)

        if genre is not None and my_id is not None:
            html_id = f" id=\"{genre}_{my_id}\""
        elif genre is not None:
            html_id = f" id=\"{genre}\""
        else:
            html_id =""

        my = []
        if genre == "avis":
            my.append(f"article_avis")
        if genre == "encart":
            my.append(f"article_encart")  

        if case is not None:
            my.append(f"col-md-{case}")
        for i in x:
            if 'case' in i:
                my.append(f"col-md-{i[1]}")
            elif 'offset' in i and int(i[1]) > 0:
                my.append(f"offset-md-{i[1]}")

        if len(my) != 0:
            txt = f"<div{html_id} class=\"{' '.join(my)}\">\n"
        else:
            txt = f"<div{html_id}>\n"

        return txt

    def create_paragraphe(self, txt):
        p = txt.split(":::")
        title = None
        if len(p) > 1:
            title = p[0]
            txt = p[1]
        else:
            txt = p[0]

        paragraphe = ""
        if title is not None:
            paragraphe += f"\t<h1>{title}</h1>\n"
        paragraphe += f"\t<p>{txt}</p>\n"

        return paragraphe

    def create_encart(self, my_id):
        paragraphe = self.config['encarts'][my_id]
        txt = ""
        p = paragraphe.split(":::")
        s = p[1].split("\n")
        if p[0] != "none":
            title = p[0]
            txt += f"\t\t\t<h1>{title}</h1>"

        text = s[0]
        photos = s[1:]

        txt += f"\t\t\t<p>{text}</p>"

        if len(photos) > 0 and len(photos) < 5:
            txt += "<div class=\"row\">"
            i = 1
            case_photo = round(12/len(photos))
            for photo in photos:
                txt += f"<div class=\"col-md-{case_photo}\">"
                link = f"encart-{my_id}_{i}.avif"
                txt += self.create_photo(i, text=photo, name=link)
                txt += "</div>"  
                i += 1
            txt += "</div>"


        return txt

    def create_avis(self, txt):
        p = txt.split(":::")
        tester = None
        avis = None

        if len(p) == 1:
            txt = p[0]

        elif len(p) == 2:
            tester =  p[0]
            txt = p[1]
        elif len(p) == 3:
            tester =  p[0]
            avis = p[1]
            txt = p[2]

        my_div = f"\t<h1>Avis"
        if tester is not None:
            my_div += f" de <span class=\"avis_tester\">{tester}</span>"
        if avis is not None:
            my_div += f" <span class=\"avis_advice\">{avis}</span>"
        my_div += "</h1>\n"
        my_div += f"\t<p>{txt}</p>\n"

        return my_div

    def create_photo(self, my_id, text=None, name=None):
        link = self.config['prop']['link_image']
        if text == None:
            photo = self.config['photos'][my_id]
            link += self.config['prop']['name_image']+"_"+my_id+".jpg"
        else:
            photo = text
            link += name

        static = "{static}"
        return f"""
            <figure class="figure">
                <img
                    class="figure-img img-fluid rounded"
                    src="{link}"
                    alt="{photo.replace('"', "'")}" 
                />
                <figcaption>{photo}</figcaption>
            </figure>
        """

    def create_preface(self):
        i = re.findall(r"(@-- preface[\w\s=]+--@)", self.template)
        my_div = self.search_el(i[0], genre="preface")
        my_div += f"\t<p>{self.config['article']['preface']}</p>\n"
        my_div += "</div>\n"

        pattern = f"@-- preface[\w\s=]+--@"
        self.template = re.sub(pattern, my_div, self.template)

    def create_plus_moins(self):
        table = "\t<table class=\"table score_table\">\n"
        table +=  "\t\t<tr class=\"tr_master\">\n"
        table += f"\t\t\t<th>Les Plus</th>\n"
        table += f"\t\t</tr>\n"
        for key, value in self.config.items('plus'):
            table +=  "\t\t<tr class=\"tr_master\">\n"
            table += f"\t\t\t<td class=\"article_plus\">{value}</td>\n"
            table += f"\t\t</tr>\n"
        table +=  "\t\t<tr class=\"tr_master\">\n"
        table += f"\t\t\t<th>Les Moins</th>\n"
        table += f"\t\t</tr>\n"
        for key, value in self.config.items('moins'):
            table +=  "\t\t<tr class=\"tr_master\">\n"
            table += f"\t\t\t<td class=\"article_moins\">{value}</td>\n"
            table += f"\t\t</tr>\n"

        table += "\t</table>\n"
        
        return table
        
    def create_note(self):
        table = "\t<table class=\"table score_table\">\n"
        for key, value in self.config.items('notes'):
            score = value.split(":::")
            note = score[0].replace('/100', '%')
            avis = None
            if len(score) > 1:
                avis = score[1]

            table +=  "\t\t<tr class=\"tr_master\">\n"
            table += f"\t\t\t<td>{key.capitalize()}</td>\n"
            table += f"\t\t\t<td class=\"artlice_score\">{note}</td>\n"
            table += f"\t\t</tr>\n"
            if avis is not None:
                table += f"\t\t<tr>\n"
                table +=f"\t\t\t<td colspan=\"2\">{avis}</td>\n"
                table += f"\t\t</tr>\n"

        table += "\t</table>\n"

        return table

    def create_link(self, text=""):
        my_div = self.search_el(text, case=12)
        if self.info_type == 'game':
            my_div += f"\t<a href=\"{self.config['magazine']['link']}\">{self.config['magazine']['title']} numero {self.config['magazine']['numero']}</a>"
            my_div += " sur <a href=\"https://www.abandonware-magazines.org/index.php\">Abandonware Magazines</a> >> "

            links = self.config['article']['links'].split(":::")

            i = 1
            for link in links:
                my_div += f"<a href=\"{link}\">page {i}</a>\n"

                if i != len(links):
                    my_div += " | "
                i += 1


        my_div += "</div>\n"
        return my_div

    def _create_link(self):
        i = re.findall(r"(@-- add_link[\w\s=]+--@)", self.template)
        my_div = self.create_link(i[0])

        pattern = f"@-- add_link[\w\s=]+--@"
        self.template = re.sub(pattern, my_div, self.template)

    def create_my_div(self, regex, txt):
        i = re.findall(regex, self.template)
        my_div = self.search_el(i[0])
        my_div += f"\t{txt}\n"
        my_div += "</div>"
        self.template = re.sub(regex, my_div, self.template)

    def create_tacklist(self):
        txt = "\t<div class=\"article_tracklist\">\n"
        txt += "\t\t<h5>Tracklist</h5>\n"
        txt += "\t\t<ul class=\"list-group\">\n"
        for key, track in self.config.items('tracklist'):
            txt += f"\t\t\t<li class=\"list-group-item list-group-item-dark\">{key}. {track}</li>\n"
        txt += "\t\t</ul>\n"
        txt += "\t</div>\n"

        return txt

    def return_template(self):
        regex = {
            'game.title': r"(@--\s?game.title[\w\s=]+--@)",
            'album.title': r"(@--\s?album.title[\w\s=]+--@)",
            'game.notes.pm': r"(@--\s?game.notes.pm[\w\s=]+--@)",
            'album.tacklist': r"(@--\s?album.tacklist[\w\s=]+--@)",
            'paragraphe': r"(@--\s?paragraphe=(\d+) ([\w\s=]+)?--@)"
        }
        if re.search(regex['game.title'], self.template):
            txt = self.create_title_article(my_type='html')
            self.create_my_div(regex['game.title'], txt)

        if re.search(regex['album.title'], self.template):
            txt = self.create_title_album()
            self.create_my_div(regex['album.title'], txt)

        if re.search(regex['album.tacklist'], self.template):
            txt = self.create_tacklist()
            self.create_my_div(regex['album.tacklist'], txt)

        if re.search(regex['paragraphe'], self.template):
            i = re.findall(regex['paragraphe'], self.template)
            for paragraphe in i:
                my_div = self.search_el(paragraphe[0], genre="paragraphe", my_id=paragraphe[1])
                my_div += self.create_paragraphe(self.config['paragraphes'][paragraphe[1]])
                my_div += "</div>"
                pattern = f"@-- paragraphe={paragraphe[1]} ([\w\s=]+)?--@"
                self.template = re.sub(pattern, my_div, self.template)

        if re.search(regex['game.notes.pm'], self.template):
            txt = self.create_note()
            txt += self.create_plus_moins()
            self.create_my_div(regex['game.notes.pm'], txt)

        if re.search(r"@-- avis=(\d+)[\w\s=]+--@", self.template):
            i = re.findall(r"(@-- avis=(\d+)[\w\s=]+--@)", self.template)
            for avis in i:
                my_div = self.search_el(avis[0], genre="avis", my_id=avis[1])
                my_div += self.create_avis(self.config['avis'][avis[1]])
                my_div += "</div>"
                pattern = f"@-- avis={avis[1]}[\w\s=]+--@"
                self.template = re.sub(pattern, my_div, self.template)

        if re.search(r"@-- game.notes[\w\s=]+--@", self.template):
            i = re.findall(r"(@-- game.notes[\w\s=]+--@)", self.template)
            my_div = self.search_el(i[0], genre="notes")
            my_div += self.create_note()
            my_div += "</div>"
            pattern = f"@-- game.notes[\w\s=]+--@"
            self.template = re.sub(pattern, my_div, self.template)

        if re.search(r"@-- photo=(\d+)[\w\s=]+--@", self.template):
            i = re.findall(r"(@-- photo=(\d+)[\w\s=]+--@)", self.template)
            for photo in i:
                my_div = self.search_el(photo[0], genre="photo", my_id=photo[1])
                my_div += self.create_photo(photo[1])
                my_div += "</div>"
                pattern = f"@-- photo={photo[1]}[\w\s=]+--@"
                self.template = re.sub(pattern, my_div, self.template)

        if re.search(r"@-- encart=(\d+)[\w\s=]+--@", self.template):
            i = re.findall(r"(@-- encart=(\d+)[\w\s=]+--@)", self.template)
            for encart in i:
                my_div = self.search_el(encart[0], genre="encart", my_id=encart[1])
                my_div += self.create_encart(encart[1])
                my_div += "</div>"
                pattern = f"@-- encart={encart[1]}[\w\s=]+--@"
                self.template = re.sub(pattern, my_div, self.template)

        if re.search(r"@-- preface[\w\s=]+--@", self.template):
            self.create_preface()

        if re.search(r"@-- add_link[\w\s=]+--@", self.template):
            self._create_link()

        return ''.join(('<article>',self.template,'\n</article>'))

    def export_pelican(self):
        title = self.create_title_article(my_type="md")
        tags = self.config['jeux']['tags'].replace(":::", ", ")
        category = self.config['article']['category']
        txt = self.return_template()

        return f"""
        <html>
            <head>
                <title>{title}</title>
                <meta name="tags" content="{tags}" />
                <meta name="date" content="{strftime("%Y-%m-%d %H:%M", gmtime())}" />
                <meta name="category" content="{category}" />
                <meta name="authors" content="VianneyBa" />
            </head>

            <body>
                {txt}
            </body>
        </html>
        """

class Export:
    def __init__(self, class_article):
        self.class_article = class_article
        self.config = configparser.ConfigParser(interpolation=None)
        self.url = "magazine/article/"

    def save_ini(self):
        with open(f"{self.url}{self.config['info']['id']}.ini", "w") as configfile:
            self.config.write(configfile)

    def create_ini(self, txt):
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        name = ''.join(secrets.choice(alphabet) for i in range(12))
        print(f"password= {name}")
        self.write_file(name, txt)


        self.config.read(f"{self.url}{name}.ini")
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
            chroniqueur = self.config['article']['chroniqueur']
            preface = self.config['paragraphes']['1']

            slug = slugify(f"{band} {title} {year} {title_site} {chroniqueur}")

        try:
            self.article = self.class_article.objects.get(slug=slug)
        except ObjectDoesNotExist:
            self.article = self.class_article(
                slug=slug,
                preface=preface,
                title_mag=title_mag,
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
