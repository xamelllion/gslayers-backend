from rest_framework import serializers
from .models import Game, Teams, Players


class TeamSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='commandId')

    class Meta:
        model = Teams
        fields = ('id', 'lobbyId', 'name', 'points', \
                    'players', 'guessing', 'explaining')
