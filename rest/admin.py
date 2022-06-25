from django.contrib import admin
from . import models

admin.register(models.Game)
admin.register(models.Teams)
admin.register(models.Players)