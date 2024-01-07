from django.db import models

class Core(models.Model):
    name = models.CharField('Nom:', max_length=100)
    command = models.CharField('Commande:', max_length=100, default='')

    def __str__(self):
        return f'{self.command} = {self.name}'


class ExecModel(models.Model):
    name = models.CharField(max_length=50, default='')
    core = models.ForeignKey(Core, on_delete=models.CASCADE)
    path = models.CharField(null=True, max_length=150)

    def __str__(self):
        return f'{self.name} avec {self.core.name}'


class System(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField('Titre:', max_length=100)

    def __str__(self):
        return f'{self.title}'


class Game(models.Model):
    name = models.CharField(max_length=50)
    desc = models.TextField(null=True, blank=True)
    image = models.CharField(null=True, max_length=100, blank=True)
    rating = models.FloatField(null=True, blank=True)
    releasedate = models.DateField(null=True, blank=True)
    genre = models.CharField(null=True, max_length=30, blank=True)
    developper = models.CharField(null=True, max_length=30, blank=True)
    publisher = models.CharField(null=True, max_length=30, blank=True)
    region = models.CharField(null=True, max_length=10, blank=True)
    players = models.PositiveIntegerField(null=True, blank=True)
    path = models.CharField(null=True, max_length=150)
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    sc_id = models.IntegerField(default=0)
    # exec_model = models.ForeignKey(ExecModel, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.name} [{self.system}]'

    def get_command_line(self):
        path_core = '/usr/lib/x86_64-linux-gnu/libretro/'

        if self.exec_model.core.command == 'retroarch':
            command = 'retroarch -fv -L'
            path_core = f'{path_core}{self.exec_model.core.name}'
            path_rom = f'\'{self.exec_model.path}{self.path}\''
            command_line = f'{command} {path_core} {path_rom}'
        elif self.exec_model.core.command == 'amiga':
            command = 'fs-uae'
            path_rom = f'\'{self.exec_model.path}{self.path}\''
            command_line = f'{command} {path_rom}'
        elif self.exec_model.core.command == 'switch':
            command = '/media/vianney/9652ebcd-97f2-40db-bb3c-33a810ed6f40/vianney/jeux/Programme/yuzu-20220416-3af07cfab.AppImage'
            path_rom = f'\'{self.exec_model.path}{self.path}\''
            command_line = f'{command} {path_rom}'
        elif self.exec_model.core.command == 'psp':
            command = 'ppsspp'
            path_rom = f'\'{self.exec_model.path}{self.path}\''
            command_line = f'{command} {path_rom}'
        elif self.exec_model.core.command == 'pc_wine':
            command_line = f'playonlinux --run "{self.path}"'
        elif self.exec_model.core.command == 'gamecube':
            path_rom = f'\'{self.exec_model.path}{self.path}\''
            command_line = f'dolphin-emu -b -e {path_rom}'

        return command_line

    class Meta:
        ordering = ['-id']