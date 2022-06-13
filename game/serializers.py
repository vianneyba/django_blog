from rest_framework import serializers
from game.models import Game, ExecModel, Core, System

class SystemSerializer(serializers.ModelSerializer):
     class Meta:
        model = System
        fields = '__all__'

class CoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Core
        fields = '__all__'

class ExecModelSerializer(serializers.ModelSerializer):
    core = CoreSerializer()
    class Meta:
        model = ExecModel
        fields = ['core', 'path']

class GameSerializer(serializers.ModelSerializer):
    # exec_model = ExecModelSerializer(read_only=True)
    system = SystemSerializer()
    command_line = serializers.SerializerMethodField('get_command_line')

    def get_command_line(self, game):
        return game.get_command_line()

    class Meta:
        model = Game
        fields = [
            'pk', 'name', 'desc', 'image', 'rating', 'releasedate',
            'genre', 'developper', 'publisher', 'region', 'players',
            'system', 'command_line']