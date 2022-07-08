from string import ascii_lowercase
from random import choices
from uuid import uuid4

from django.forms.models import model_to_dict

from .models import Game, Teams, Players


def create_code():
    code = choices(list(ascii_lowercase), k=8)
    return ''.join(code)

def generate_unique_id():
    return str(uuid4())


def build_players_object(players, lobbyAdmin=None):
    obj = {}
    check = True
    admin = ''

    if lobbyAdmin is None:
        check = False

    for element in players:
        element = model_to_dict(element)
        playerId = element['playerId']

        del element['id']
        if element['team'] == 'None':
            element['team'] = None
        del element['lobbyId']
        element['id'] = playerId
        del element['playerId']

        obj[playerId] = element

        if element['id'] != lobbyAdmin and check == True:
            admin = element['id']
        else:
            check = False
    
    if check:
        lobbyAdmin = admin

    return obj, lobbyAdmin


def build_team_list(teams):
    team_list = []
    for element in teams:
        element = model_to_dict(element)
        commandId = element['commandId']
        del element['commandId']
        element['id'] = commandId
        team_list.append(element)

    if len(team_list) == 0:
        commandId = generate_unique_id()
        team_list = [
            {
                'id': commandId,
                'name': '',
                'points': 0,
                'players': {
                    0: None,
                    1: None,
                },
                'guessing': 0,
                'explaining': 1,
            }
        ]
    return team_list


def build_ws_object(lobbyId):
    game = Game.objects.get(lobbyId=lobbyId)
    players = Players.objects.filter(lobbyId=lobbyId)
    teams = Teams.objects.filter(lobbyId=lobbyId)

    players_obj, lobbyAdmin = build_players_object(players, game.lobbyAdmin)
    teams_list = build_team_list(teams)
    
    game.lobbyAdmin = lobbyAdmin
    game.save()
    
    return {
        'admin': game.lobbyAdmin,
        'settings': game.settings,
        'teams': teams_list,
        'players': players_obj
    }


def on_player_disconnect(playerId):
    p = Players.objects.get(playerId=playerId)
    lobbyId = p.lobbyId
    p.delete()

    try:
        t = Teams.objects.get(lobbyId=lobbyId)
        obj = t.players

        for key, value in obj.items():
            if value == playerId:
                obj[key] = None
                break

        t.players = obj
        t.save()
    except Exception:
        pass
