from django.urls import path
from . import views

urlpatterns = [
    path('api/createLink/', views.createLink),
    path('', views.home),
    path('alias/', views.lobbyExist)
]