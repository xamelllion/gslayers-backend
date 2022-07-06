from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('api/createLink/', views.createLink),
    path('alias/', views.lobbyExist),
    path('words/', views.fetchWords)
]