from django.contrib import admin
from game.models import Game, System, Core, ExecModel

class GameAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'path')

admin.site.register(Game, GameAdmin)
admin.site.register(System)
admin.site.register(Core)
admin.site.register(ExecModel)
