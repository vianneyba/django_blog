import os
import re
import requests
import json
from slugify import slugify
from requests.structures import CaseInsensitiveDict
import argparse
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

class System:

    list_system = []

    def __init__(self, pk, slug, title):
        self.id = pk
        self.slug = slug
        self.title = title
        self.list_system.append(self)

    @classmethod
    def search_by_name(cls, title):
        for system in cls.list_system:
            if system.title == title:
                return system
        return None

    @classmethod
    def search_by_id(cls, pk):
        for system in cls.list_system:
            if system.id == int(pk):
                return system
        return None
    
    @classmethod
    def get_all_title(cls):
        titles = []
        for system in cls.list_system:
            titles.append(system.title)
        return titles

    @classmethod
    def get_list_system(cls):
        return cls.list_system

class Game:

    list_game = []

    def __init__(self, pk, name, command_line):
        if self.search_by_id(pk) is None:
            self.id = pk
            self.name = name
            self.command_line = command_line
            self.list_game.append(self)
            self.system = None

    def add_system(self, id_system):
        self.system = System.search_by_id(id_system)

    @classmethod
    def search_by_id(cls, pk):
        for game in cls.list_game:
            if game.id == int(pk):
                return game
        return None

    @classmethod
    def search_by_system(cls, system):
        list_game = []
        for game in cls.list_game:
            if game.system.slug == system.slug:
                list_game.append(game)
        
        return list_game
    
    @classmethod
    def search_game(cls, word):
        list_game = []
        for game in cls.list_game:
            if word.lower() in game.name.lower():
                list_game.append(game)
        return list_game

    @classmethod
    def search_by_name_system(cls, name, system):
        for game in cls.list_game:
            if game.name == name and game.system.title == system:
                return game

class Article:
    def __init__(self, title, content, category):
        self.id = None
        self.title = title
        self.content = content
        self.slug = slugify(title)
        # created_at = models.DateTimeField(default=timezone.now)
        # published = models.BooleanField(default=False)
        # update_date = models.DateTimeField(default=None, blank=True)
        # author = models.ForeignKey(User, on_delete=models.CASCADE)
        self.category = category
        # like_count = models.IntegerField(default=0)
        # dislike_count = models.IntegerField(default=0)
        self.tags = []

    def add_tag(self, tag):
        if isinstance(tag, list):
            self.tags = tag
        else:
            self.tags.append(tag)

    def get_json(self):
        return {
            'title': self.title,
            'content': self.content,
            'slug': self.slug,
            'category': self.category,
            'tags': ';'.join(self.tags)
        }
    
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

def read_file(file):
    with open(file) as f:
        lines = f.readlines()

    regex = ': *([\w,&+ -]*)'
    content = ''

    for line in lines:
        if re.search(f'Title{regex}', line) is not None:
            title = re.search(f'Title{regex}', line).group(1)
        elif re.search(f'Date{regex}', line) is not None:
            date_created = re.search(f'Date{regex}', line).group(1)
        elif re.search(f'Modified{regex}', line) is not None:
            date_updated = re.search(f'Modified{regex}', line).group(1)
        elif re.search(f'Category{regex}', line) is not None:
            category = re.search(f'Category{regex}', line).group(1)
        elif re.search(f'Tags{regex}', line) is not None:
            tags = re.search(f'Tags{regex}', line).group(1)
            tags = tags.split(', ')
        elif re.search(f'Slug{regex}', line) is not None:
            slug = re.search(f'Slug{regex}', line).group(1)
        elif re.search(f'Summary{regex}', line) is not None:
            summary = re.search(f'Summary{regex}', line).group(1)
        elif re.search(f'Authors{regex}', line) is not None:
            authors = re.search(f'Authors{regex}', line).group(1)
        else:
            content += line

    article = Article(title, content, category)
    article.add_tag(tags)

    return article    

class Client_Api:
    def __init__(self, debug=False):
        if debug:
            self.base_url = 'https://vianneyba.pythonanywhere.com/api'
        else:
            self.base_url = 'http://localhost:8082/api'
        self.token = None
        self.debug = debug

    def create_header(self):
        self.headers = CaseInsensitiveDict()
        self.headers["Accept"] = 'application/json'
        self.headers["Authorization"] = f"Bearer {self.token}"

    def jprint(self, obj):
        text = json.dumps(obj, sort_keys=True, indent=4)
        print(text)

    def get_token(self, user):
        url = f'{self.base_url}/token/'
        self.user = user
        data = {
            'username': self.user.username,
            'password': self.user.password}

        response = requests.post(url, data=data)

        if response.status_code == 200:
            self.token = response.json()['access']
            self.create_header()

        return {
            'status_code': response.status_code
        }

    def get_article(self):
        url = f'{self.base_url}/articles/'
        response = requests.get(url)

    def get_game(self, pk):
        url = f'{self.base_url[:-4]}/launch-game/api/games/{pk}/'
        response = requests.get(url)
        command_line = response.json()['command_line']
        os.system(command_line)

    def get_list_game(self, system=None, game=None):
        url = f'{self.base_url[:-4]}/launch-game/api/games/'
        if system is not None:
            url += f'?system={system}'
        if game is not None:
            url += f'?game={game}'
            
        response = requests.get(url)

        for game in response.json():
            new = Game(game['pk'], game['name'], game['command_line'])
            new.add_system(game['system']['id'])

        return Game.list_game

    def get_system(self):
        url = f'{self.base_url[:-4]}/launch-game/api/systems/'
        response = requests.get(url)
        for system in response.json()['results']:
            System(system['id'], system['slug'], system['title'])
        return System.get_list_system()

    def add_article(self, article):
        url = f'{self.base_url}/articles/'
        response = requests.post(url,data=article.get_json(),
            headers=self.headers)

        if response.status_code == 201:
            article.id = response.json()['id']

class window_game:
    def __init__(self, win):
        self.win = win
        self.client_api = Client_Api(debug=True)
        self.client_api.get_system()
        self.view_system(row=0, col=0)
        self.view_list_game(row=0, col=1) 
        self.get_list_game()
        self.entry_search(row=1, col=0)

    def view_system(self, row=0, col=0):
        frame = LabelFrame(self.win, text="System")
        self.selected_system = StringVar()
        self.option = ttk.Combobox(frame, values=System.get_all_title(), textvariable=self.selected_system)
        self.option.current(0)
        self.option.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.option.bind('<<ComboboxSelected>>', self.callback_system_changed)
        frame.grid(row=row, column=col, sticky="nsew")

    def view_list_game(self, row=0, col=1, rowspan=10):
        columns = ('title', 'system')
        self.list_game = ttk.Treeview(root, columns=columns, show='headings', selectmode='browse')
        self.list_game.heading('title', text='Titre')
        self.list_game.heading('system', text='System')
        self.list_game.column('title', minwidth=250, width=300, stretch=NO) 
        self.list_game.column('system', minwidth=150, width=190)
        self.list_game.bind('<<TreeviewSelect>>', self.callback_list_game)

        scrollbar = ttk.Scrollbar(root, orient=VERTICAL, command=self.list_game.yview)
        self.list_game.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=row, column=col+1,rowspan=rowspan, sticky='ns')
        self.list_game.grid(row=row, column=col, rowspan=rowspan, sticky='nsew')

    def entry_search(self, row=0, col=0):
        frame = LabelFrame(self.win, text="Recherche")
        label_search = Label(frame, text='recherche: ')
        self.entry_search = Entry(frame, textvariable='')
        self.entry_search.bind('<Return>', self.callback_search_game)

        frame.grid(row=row, column=col, sticky="nsew")
        label_search.grid(row=0, column=0, sticky="nsew")
        self.entry_search.grid(row=1, column=0, sticky="nsew")


    def get_list_game(self):
        self.clear_list_game()
        games = self.client_api.get_list_game()
        self.change_list_game(games)

    def clear_list_game(self):
        for item in self.list_game.get_children():
            self.list_game.delete(item)

    def callback_system_changed(self, event):
        name = self.selected_system.get()
        system = System.search_by_name(name)
        self.client_api.get_list_game(system=system.slug)
        games = Game.search_by_system(system)
        self.change_list_game(games)

    def callback_list_game(self, event):
        item = self.list_game.item(self.list_game.selection())
        record = item['values']
        game = Game.search_by_name_system(record[0], record[1])
        print(game.command_line)
        os.system(game.command_line)

    def callback_search_game(self, event):
        word = self.entry_search.get()
        self.client_api.get_list_game(game=word)
        games = Game.search_game(word)
        self.change_list_game(games)

    def change_list_game(self, games):
        self.clear_list_game()
        for game in games:
            info_game = (game.name, game.system.title)
            self.list_game.insert('', END, values=info_game)

root = Tk()
root.title('Vianney Game')
root.geometry('700x300')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', type=int, required=False)
    args = parser.parse_args()

    # user = User('vianney', '4fU1TLGv')
    # client_api.get_token(user)
    # client_api.add_article(read_file('/home/vianney/Documents/test Jeux/Banjo & Kazooie [N64] Console+ 079.txt'))
    # client_api.get_article()

    if args.game is not None:
        client_api.get_game(args.game)
    else:
        window_game(root)
        root.mainloop()

    # http://localhost:8082/api/launch-game/api/games/1/
    # http://localhost:8082/launch-game/api/games/1/