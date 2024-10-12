from django.core.exceptions import ObjectDoesNotExist
import requests
from bs4 import BeautifulSoup
import os

def import_test_from_am(id_mag, mag, num):
    url = f'https://www.abandonware-magazines.org/affiche_mag.php?mag=&num={id_mag}&album=oui'
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
 
    my_text = url

    links = soup.find_all('a')
    for link in links:
        if link.get("href") is not None and ".jpg" in link.get("href"):
            link = link.get("href")
            filedata = link.get("href").replace(' ', '%20')
            filedata = link.get("href").replace('(', '%28')
            filedata = link.get("href").replace(')', '%29')
            my_text = f'{my_text}\n{filedata};'

    f = open(f"magazine/magazines/{mag}_{num}.txt", "w")
    f.write(my_text)
    f.close()

def import_page(models, id_mag, title_mag, num_mag):
    file_txt = f"magazine/magazines/{title_mag}_{num_mag}.txt"
    if os.path.exists(file_txt) == False:
        import_test_from_am(id_mag, title_mag, num_mag)

    f = open(file_txt, "r")
    i = 0
    for x in f:
        if i == 0:
            try:
                magazine = models.Magazine.objects.get(url=x)
            except ObjectDoesNotExist:
                magazine = models.Magazine(
                    url=x,
                    title_mag=title_mag,
                    num_mag=num_mag)
                magazine.save()

        else:
            line = x.split(";")
            games = line[1].split(':::')

            for game in games:
                page = models.Page(
                    title_game=game.strip(),
                    url=line[0],
                    magazine=magazine)
                page.save()
        i = i + 1

    return magazine