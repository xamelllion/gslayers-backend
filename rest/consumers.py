import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from .stuff import build_players_object
from .models import Game, Teams, Players

from .stuff import build_ws_object, on_player_disconnect, remove_old_teams


class ChatConsumer(WebsocketConsumer):

    lobbyId = ''

    def connect(self):
        global lobbyId
        info = self.scope['url_route']['kwargs']['info']
        lobbyId, playerId = info.split('_')

        self.room_name = playerId
        self.room_group_name = lobbyId
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        # g = Game.objects.get(lobbyId=lobbyId)
        players = Players.objects.filter(lobbyId=lobbyId)
        p, _ = build_players_object(players)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
            'type': 'broadcast',
            'data': {
                'players': p
            },
            'sender_channel_name': self.channel_name
            }
        )
    

    def disconnect(self, close_code):

        # remove player from players and teams objects
        on_player_disconnect(self.room_name)
        d = build_ws_object(lobbyId)
        print('Отправил после disconnect:', d)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
            'type': 'broadcast',
            'data': d,
            'sender_channel_name': self.channel_name
            }
        )
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


    def receive(self, text_data):
        print('Пришло', text_data)
        print('--------------------')
        text_data = json.loads(text_data)
        g = Game.objects.get(lobbyId=lobbyId)
        if 'settings' in text_data:
            g.settings = text_data['settings']
            g.save()
        if 'entities' in text_data:
            e = text_data['entities']
            for k, v in e.items():
                try:
                    p = Players.objects.get(playerId=k)
                    p.lobbyId = lobbyId
                    p.name = v['name']
                    p.team = str(v['team'])
                    p.save()
                except Exception:
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
            
            # remove teams from db whitch was removed by user
            remove_old_teams(text_data['teams'], lobbyId)
        
        
        
        if 'ids' in text_data.keys():
            del text_data['ids']
        if 'entities' in text_data.keys():
            text_data['players'] = text_data['entities']
            del text_data['entities']
        d = text_data
        
        # d = build_ws_object(lobbyId)
        print('Отправил', d)
        print('--------------------')

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
            'type': 'broadcast',
            'data': d,
            'sender_channel_name': self.channel_name
            }
        )
    
    
    def broadcast(self, event):
        # print(event)
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=json.dumps({
                'data': event['data']
            }))
    
    def new_player_connect(self, event):
        print('New player event')
        print(event)
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=json.dumps({
                'players': event['players']
            }))
