from django.shortcuts import render, HttpResponse
from django.http import JsonResponse, FileResponse

from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json
from string import ascii_lowercase
from random import choices

from .models import Game

def create_code():
    a = choices(list(ascii_lowercase), k=8)
    return ''.join(a)


@csrf_exempt
def gen(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)

        '''
        need to create 'lobby'
        '''

        lobby_code = create_code()

        lobby_link = f"{request.scheme}://{request.META['HTTP_HOST']}/alias/?lobby={lobby_code}"
        player_code = create_code()

        game = Game(
            lobby_id=lobby_code,
            status=data['status'],
            settings=json.dumps(data['settings'])
            )
        game.save()

        return JsonResponse({
            'lobbyId': lobby_code,
            'lobbyLink': lobby_link,
            'playerId': player_code
        })


def home(request):
    return HttpResponse('dick')


@csrf_exempt
def alias(request):
    a = request.GET
    if 'lobby' not in request.GET:
        return JsonResponse({'error': 1})
    
    code = request.GET['lobby']

    g = Game.objects.filter(lobby_id=code)

    if len(g) == 0:
        return JsonResponse({'exist': False})
    
    return JsonResponse({'exist': True})