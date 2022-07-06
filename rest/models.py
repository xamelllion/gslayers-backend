
from django.db import models
from django.db.models import JSONField

class Game(models.Model):
    lobbyId = models.CharField(max_length=36)
    lobbyAdmin = models.CharField(max_length=36)
    settings = JSONField()


class Teams(models.Model):
    lobbyId = models.CharField(max_length=36)
    commandId = models.CharField(max_length=36)
    name = models.CharField(max_length=36)
    points = models.IntegerField()
    players = JSONField()
    guessing = models.IntegerField()
    explaining = models.IntegerField()


class Players(models.Model):
    lobbyId = models.CharField(max_length=36)
    playerId = models.CharField(max_length=36)
    name = models.CharField(max_length=36)
    team = models.CharField(max_length=36)


class Words(models.Model):
    mode = models.CharField(max_length=36)
    word = models.CharField(max_length=256)