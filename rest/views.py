from django.shortcuts import HttpResponse
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
import json

from .models import Game, Teams, Players, Words
from .stuff import create_code, generate_unique_id
from .stuff import build_players_object, build_team_list, remove_old_data


from .serializers import TeamSerializer

from rest_framework.response import Response

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
import os


@csrf_exempt
def clean(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        if data['key'] == os.environ.get('KEY'):
            remove_old_data()
        return JsonResponse({'code': 1})
    return JsonResponse({'code': 0})



def home(request):
    return HttpResponse('dick')


@csrf_exempt
def lobbyExist(request):
    
    if 'newLobby' in request.GET:
        
        while True:
            lobbyId = create_code()
            check_lobby = Game.objects.filter(lobbyId=lobbyId)
            if len(check_lobby) == 0: break

        game = Game(
            lobbyId=lobbyId,
            settings={'points': 30, 'time': 30, 'mode': 'medium'},
            creationTime=datetime.now()
        )
        game.save()

        name = request.GET['name']
        
        playerId = generate_unique_id()

        player = Players(
            lobbyId=lobbyId,
            playerId=playerId,
            name=name,
            team='None'
        )
        player.save()
        
        
        game.lobbyAdmin = playerId
        game.save()

        players = Players.objects.filter(lobbyId=lobbyId)
        teams = Teams.objects.filter(lobbyId=lobbyId)

        players_obj, lobbyAdmin = build_players_object(players, game.lobbyAdmin)
        teams_list = build_team_list(teams)

        game.lobbyAdmin = lobbyAdmin
        game.save()

        return JsonResponse({
            'currentPlayer': playerId,
            'lobbyId': lobbyId,
            'admin': lobbyAdmin,
            'settings': game.settings,
            'teams': teams_list,
            'players': players_obj   
        })



    if 'lobby' in request.GET:
        lobbyId = request.GET['lobby']
        name = request.GET['name']

        try:
            game = Game.objects.get(lobbyId=lobbyId)
        except Exception:
            return JsonResponse({'exist': False, 'data': {}})
        
        
        playerId = generate_unique_id()
        
        players = Players.objects.filter(lobbyId=lobbyId)

        if len(players) == 0:
            game.lobbyAdmin = playerId
            game.save()

        player = Players(
            lobbyId=lobbyId,
            playerId=playerId,
            name=name,
            team='None'
        )
        player.save()
        

        players = Players.objects.filter(lobbyId=lobbyId)
        teams = Teams.objects.filter(lobbyId=lobbyId)

        # serializer = TeamSerializer(teams, many=True)
        # print(serializer.data)

        players_obj, lobbyAdmin = build_players_object(players, game.lobbyAdmin)
        teams_list = build_team_list(teams)
        print(teams_list)

        game.lobbyAdmin = lobbyAdmin
        game.save()

        return JsonResponse({
            'exist': True,
            'data': {
                'currentPlayer': playerId,
                'lobbyId': lobbyId,
                'admin': lobbyAdmin,
                'settings': game.settings,
                'teams': teams_list,
                'players': players_obj
            }
        })


def fetchWords(request):
    lobbyId = request.GET['lobby']
    if 'wordsFetched' in request.GET and \
         request.GET['wordsFetched'] == 'true':

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            lobbyId,
            {
                'type': 'broadcast',
                'data': {'wordsSettled': True},
                'sender_channel_name': ''
            }
        )
        return JsonResponse({})
        
    
    game = Game.objects.get(lobbyId=lobbyId)
    mode = game.settings['mode']

    words = [query.word for query in Words.objects.filter(mode=mode)]

    return JsonResponse({'words': words})