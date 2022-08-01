from django.contrib import admin
from . import models

admin.site.register(models.Game)
admin.site.register(models.Teams)
admin.site.register(models.Players)
admin.site.register(models.Words)