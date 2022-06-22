from django.db import models
# from django.contrib.postgres.fields import JSONField
from django.db.models import JSONField

class Game(models.Model):
    lobby_id = models.CharField(max_length=32)
    status = models.CharField(max_length=32)
    settings = JSONField()


class Teams(models.Model):
    lobby_id = models.CharField(max_length=32)
    name = models.CharField(max_length=32)
    points = models.IntegerField()
    players = JSONField()
    guessing = models.IntegerField()
    explaining = models.IntegerField()


class Players(models.Model):
    lobby_id = models.CharField(max_length=32)
    is_admin = models.CharField(max_length=32)
    player_id = models.CharField(max_length=32)
    status = models.CharField(max_length=32)
    team = models.CharField(max_length=32)