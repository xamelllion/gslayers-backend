from cgitb import text
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from .stuff import build_players_object, build_team_list
from .models import Game, Teams, Players

from .stuff import create_code


class ChatConsumer(WebsocketConsumer):

    lobbyId = ''

    def connect(self):
        global lobbyId
        lobbyId = self.scope['url_route']['kwargs']['lobby_id']

        self.room_group_name = lobbyId
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        # player = Players(
        #     lobbyId=lobbyId,
        #     playerId=create_code(),
        #     name='',
        #     team='None'
        # )
        # player.save()

        # self.send(text_data=json.dumps({
        #     'type': 'chat-chank',
        #     'data': ''
        # }))
        g = Game.objects.get(lobbyId=lobbyId)
        players = Players.objects.filter(lobbyId=lobbyId)
        teams = Teams.objects.filter(lobbyId=lobbyId)

        players_obj, lobbyAdmin = build_players_object(players, g.lobbyAdmin)
        teams_list = build_team_list(teams)
        
        d = {
            'admin': g.lobbyAdmin,
            'settings': g.settings,
            'teams': teams_list,
            'players': players_obj
        }

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
            'type': 'chat_message',
            'data': d
            }
        )
    
    def receive(self, text_data):
        print(text_data)
        print('--------------------')
        text_data = json.loads(text_data)
        g = Game.objects.get(lobbyId=lobbyId)
        if 'settings' in text_data:
            g.settings = text_data['settings']
            g.save()
        if 'entities' in text_data:
            e = text_data['entities']
            for k, v in e.items():

                p = Players(
                    lobbyId=lobbyId,
                    playerId=k,
                    name=v['name'],
                    team=str(v['team'])
                )
                p.save()
        if 'teams' in text_data:
            for el in text_data['teams']:
                try:
                    t = Teams.objects.get(commandId=el['id'])
                    t.commandId=el['id']
                    t.name=el['name']
                    t.points=el['points']
                    t.players=el['players']
                    t.guessing=el['guessing']
                    t.explaining=el['explaining']
                except Exception:
                    t = Teams(
                        lobbyId=lobbyId,
                        commandId=el['id'],
                        name=el['name'],
                        points=el['points'],
                        players=el['players'],
                        guessing=el['guessing'],
                        explaining=el['explaining']
                    )
                t.save()
        
        players = Players.objects.filter(lobbyId=lobbyId)
        teams = Teams.objects.filter(lobbyId=lobbyId)

        players_obj, lobbyAdmin = build_players_object(players, g.lobbyAdmin)
        teams_list = build_team_list(teams)
        # f = Game.objects.get(lobbyId=lobbyId)
        # print(f.setings)

        d = {
            'admin': g.lobbyAdmin,
            'settings': g.settings,
            'teams': teams_list,
            'players': players_obj
        }
        print(d)
        print('--------------------')

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
            'type': 'chat_message',
            'data': d
            }
        )
    
    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'data': event['data']
        }))