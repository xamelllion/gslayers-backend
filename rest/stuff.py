from string import ascii_lowercase
from random import choices
from uuid import uuid4

from django.forms.models import model_to_dict

from .models import Game, Teams, Players
from datetime import datetime


def create_code() -> str:
    '''Function generate 8 digit code code.'''
    code = choices(list(ascii_lowercase), k=8)
    return ''.join(code)


def generate_unique_id() -> str:
    '''Function generate uuid code.'''
    return str(uuid4())


def build_players_object(players, lobbyAdmin=None):
    '''
    Function that transfer players data from db to client format.
    Choose new lobbyAdmin if it needed.
    '''

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

        if element['id'] != lobbyAdmin and check is True:
            admin = element['id']
        else:
            check = False

    if check:
        lobbyAdmin = admin

    return obj, lobbyAdmin


def build_team_list(teams: list) -> list:
    '''Function that transfer team data from db to client format.'''
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


def build_ws_object(lobbyId: str) -> dict:
    '''Function collect all data that need to be sended via ws.'''
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


def on_player_disconnect(playerId: str) -> None:
    '''Function remove player from players table and from player's team.'''
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
    except Exception as e:
        print(e)


def remove_old_data() -> None:
    '''Function delete from db all data older than 1 day.'''
    games = Game.objects.all()
    current_time = datetime.now()

    for game_obj in games:
        difference = current_time - game_obj.creationTime
        if difference.days >= 1:
            lobbyId = game_obj.lobbyId

            Game.objects.get(lobbyId=lobbyId).delete()
            Players.objects.filter(lobbyId=lobbyId).delete()
            Teams.objects.filter(lobbyId=lobbyId).delete()


def remove_old_teams(teams: list, lobbyId: str) -> None:
    '''Function deleting from db teams whitch was deleted by client.'''
    teams_from_client = [x['id'] for x in teams]
    teams_from_db = Teams.objects.filter(lobbyId=lobbyId)

    for team in teams_from_db:
        if team.commandId not in teams_from_client:
            team.delete()