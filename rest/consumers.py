import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from .stuff import build_players_object
from .models import Game, Teams, Players

from .stuff import build_ws_object, on_player_disconnect, remove_old_teams

from .serializers import TeamSerializer, PlayerSerializer

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
        received_data = json.loads(text_data)

        print('Пришло', received_data)
        print('--------------------')

        g = Game.objects.get(lobbyId=lobbyId)

        if 'settings' in received_data:
            g.settings = received_data['settings']
            g.save()

        if 'entities' in received_data:
            e = received_data['entities'].copy()
            for key, value in e.items():
                value['lobbyId'] = lobbyId
                value['playerId'] = value['id']
                value['team'] = str(value['team'])
                try:
                    p = Players.objects.get(playerId=key)
                    serializer = PlayerSerializer(instance=p, data=value)
                    if serializer.is_valid():
                        serializer.save()
                except Exception:
                    serializer = PlayerSerializer(data=value)
                    if serializer.is_valid():
                        serializer.save()

        if 'teams' in received_data:
            for el in received_data['teams'].copy():
                el['lobbyId'] = lobbyId
                el['commandId'] = el['id']

                try:
                    t = Teams.objects.get(commandId=el['id'])
                    serializer = TeamSerializer(instance=t, data=el)
                    if serializer.is_valid():
                        serializer.save()

                except Exception:
                    serializer = TeamSerializer(data=el)
                    if serializer.is_valid():
                        serializer.save()
            
            # remove teams from db that was removed by user
            remove_old_teams(received_data['teams'], lobbyId)
        
        
        if 'ids' in received_data.keys():
            received_data.pop('ids')
        if 'entities' in received_data.keys():
            received_data['players'] = received_data.pop('entities')
        
        print('Отправил', received_data)
        print('--------------------')

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
            'type': 'broadcast',
            'data': received_data,
            'sender_channel_name': self.channel_name
            }
        )
    
    
    def broadcast(self, event):
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=json.dumps({
                'data': event['data']
            }))

