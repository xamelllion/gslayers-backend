from django.shortcuts import HttpResponse
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
import json

from .models import Game, Teams, Players, Words
from .stuff import create_code
from .stuff import build_players_object, build_team_list


from .serializers import TeamSerializer

from rest_framework.response import Response

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def home(request):
    return HttpResponse('dick')


@csrf_exempt
def lobbyExist(request):
    
    if 'newLobby' in request.GET:
        lobbyId = create_code()
        game = Game(
            lobbyId=lobbyId,
            settings={'points': 30, 'time': 30, 'mode': 'medium'}
        )
        game.save()

        name = request.GET['name']
        
        playerId = create_code()

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
        
        
        playerId = create_code()
        
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

        serializer = TeamSerializer(teams, many=True)
        print(serializer.data)

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
            {'type': 'broadcast', 'data': {'wordsSettled': True}}
        )
        return JsonResponse({})
        
    
    game = Game.objects.get(lobbyId=lobbyId)
    mode = game.settings['mode']

    words = [query.word for query in Words.objects.filter(mode=mode)]

    return JsonResponse({'words': words})