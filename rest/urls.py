from django.urls import path
from . import views

urlpatterns = [
    path('api/gen/', views.gen),
    path('', views.home),
    path('alias/', views.alias)
]