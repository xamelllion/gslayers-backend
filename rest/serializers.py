from rest_framework import serializers
from .models import Game, Teams, Players


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teams
        fields = '__all__'


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Players
        fields = '__all__'