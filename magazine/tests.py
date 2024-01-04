from django.test import TestCase
from game.models import Game, System
from magazine.models import Article, Paragraph


class SystemCreateTestCase(TestCase):
    def setUp(self):
        system_1 = System(
            title='Super nintendo',
            slug='snes')

        game_1 = Game(
            name='tetris battle gaiden',
            desc='grand jeux',
            system=system_1)

        game_1.save()

        article_1 = Article(
            game=game_1,
            num_page=4,
            preface="Le premier Tetris a été créé par Alexey Pajitnov, un Soviétique. Depuis, la Game Boy a largement contribué à la popularité de ce jeu adapté, bien sûr, sur toutes les consoles. Aujourd'hui, le concept du \"casse-briques\" n'a pas pris une ride. Alors, faut-il craquer pour cette nouvelle version sur SFC? Consoles+ répond!",
            slug='bo-bo',
            title_mag='console+',
            num_mag='4')

        paragraph_1 = Paragraph(
            article=article_1,
            text="Le principe de jeu n'a pas varié. Il est toujours aussi simple: du haut de l'écran tombent des pièces qu'il faut assembler comme un puzzle afin de former le maximum de lignes pleines. Mais attention, dans Tetris Battle Gaiden, il n'est plus question de jouer seul. Vous jouez soit contre la console, soit contre un copain. Et, croyez-moi, le challenge est à la hauteur, surtout contre la console en niveau Expert...<br>Il existe trois modes de jeu différents. Le mode Tetris reprend le concept de base, mais à la manière du mode 2 joueurs des versions Game Boy: dès que vous avez construit une ligne complète, elle disparaît de votre écran et se retrouve sur celui de l'adversaire. Deuxième type de jeu, le mode Battlis, dans lequel des personnages sont mis en scène et peuvent agir sur les tableaux grâce à des cristaux magiques. Une partie pleine d'humour et qui instaure une ambiance du tonnerre! Enfin, le mode Rensa est quasiment identique au précédent. Seule différence, les cristaux restent à l'endroit où ils se sont posés jusqu'à ce que vous les fassiez disparaître en les incluant dans une ligne. Côté options, Tetris Battle Gaiden est très complet, et vous propose quatre niveaux de difficulté, la possibilité de varier la vitesse de chute des pièces, etc. Du tout bon!")
    
    def test_article_can_speak(self):
        b = Game.objects.get(name='tetris battle gaiden')
        