from django.shortcuts import HttpResponse
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
import json

from .models import Game, Teams, Players
from .stuff import create_code
from .stuff import build_players_object, build_team_list


@csrf_exempt
def createLink(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)

        lobby_code = create_code()

        lobby_link = f"{request.scheme}://{request.META['HTTP_HOST']}/alias/?lobby={lobby_code}"

        game = Game(
            lobbyId=lobby_code,
            settings=data['settings']
            )
        game.save()


        print(lobby_link)
        return JsonResponse({
            'lobbyId': lobby_code,
            'lobbyLink': lobby_link
        })


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

        players_obj, lobbyAdmin = build_players_object(players, game.lobbyAdmin)
        teams_list = build_team_list(teams)


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

