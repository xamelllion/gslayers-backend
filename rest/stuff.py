from string import ascii_lowercase
from random import choices

from django.forms.models import model_to_dict


def create_code():
    code = choices(list(ascii_lowercase), k=8)
    return ''.join(code)


def build_players_object(players, lobbyAdmin):
    obj = {}
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

        if element['id'] == lobbyAdmin:
            check = True

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
        commandId = create_code()
        team_list = [
            {
                'id': commandId,
                'name': '',
                'points': 0,
                'players': {
                    0: None,
                    1: None,
                },
                'guessing': 1,
                'explaining': 2,
            }
        ]
    return team_list