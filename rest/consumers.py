import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from .stuff import build_players_object, build_team_list
from .models import Game, Teams, Players

from .stuff import create_code, build_ws_object


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

        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name,
        #     {
        #     'type': 'broadcast',
        #     'data': build_ws_object(lobbyId)
        #     }
        # )
    

    def disconnect(self, close_code):
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
            'type': 'broadcast',
            'data': build_ws_object(lobbyId)
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
        
        if 'ids' in text_data.keys():
            del text_data['ids']
        if 'entities' in text_data.keys():
            text_data['players'] = text_data['entities']
            del text_data['entities']
        d = text_data
        
        # d = build_ws_object(lobbyId)
        print(d)
        print('--------------------')

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
            'type': 'broadcast',
            'data': d
            }
        )
    
    
    def broadcast(self, event):
        self.send(text_data=json.dumps({
            'data': event['data']
        }))