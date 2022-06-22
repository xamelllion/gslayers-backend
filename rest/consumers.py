import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_group_name = 'test'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        self.send(text_data=json.dumps({
            'type': 'chat-chank',
            'data': ''
        }))
    
    def receive(self, text_data):
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
            'type': 'chat_message',
            'message_json': 'essage_json'
            }
        )
    
    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'chat',
            'text': event['message_json']['text'],
            'time': event['message_json']['time'],
            'username': event['message_json']['username']
        }))