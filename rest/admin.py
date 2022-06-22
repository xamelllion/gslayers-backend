from django.contrib import admin
from . import models
# Register your models here.

admin.register(models.Game)
admin.register(models.Teams)
admin.register(models.Players)