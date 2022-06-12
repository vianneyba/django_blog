from rest_framework import serializers
from game.models import Game, ExecModel, Core

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
    exec_model = ExecModelSerializer(read_only=True)
    command_line = serializers.SerializerMethodField('get_command_line')

    def get_command_line(self, game):
        return game.get_command_line()

    class Meta:
        model = Game
        fields = ['name', 'exec_model', 'command_line']