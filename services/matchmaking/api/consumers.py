from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from api.models.match import Match
import uuid

rooms = []


def create_room(gamer_id, channel_name, capacity, match_id):
    rooms.append({
        "gamers": [{
            gamer_id: channel_name,
        }],
        'id': str(uuid.uuid4()),
        'match_id': match_id,
        'capacity': capacity
    })
    return rooms[len(rooms) - 1]


def get_room(gamer_id, capacity, channel_name, match_id):
    for room in rooms:
        if (len(room['gamers']) < capacity and
                room['capacity'] == capacity and
                room['match_id'] == match_id):
            room['gamers'].append({gamer_id: channel_name})
            async_to_sync(get_channel_layer().group_add)(room['id'], channel_name)
            if len(room['gamers']) == capacity:
                async_to_sync(get_channel_layer().group_send)(room['id'], {
                    "type": "chat.message",
                    "text": room['id'],
                })
                rooms.remove(room)
            return
    return create_room(gamer_id, channel_name, capacity, match_id)


def find_channels_room(gamer_id, channel_name):
    for room in rooms:
        for gamer in room['gamers']:
            if gamer_id in gamer:
                if gamer[gamer_id] == channel_name:
                    room['gamers'].remove(gamer)
                return room
    return None

def match_played(match_id):
    match = Match.objects.get(id=match_id)
    return match.state == 'PLY'

class Matchmaking(WebsocketConsumer):
    def receive(self, text_data):
        print(text_data)

    def chat_message(self, event):
        self.send(text_data=event["text"])

    def connect(self):
        match_id = self.scope['url_route']['kwargs'].get('match_id')
        self.accept()
        if match_id is not None and match_played(match_id):
            self.send("ALREADY PLAYED")
            return
        if find_channels_room(self.scope['payload']['id'], self.channel_name):
            self.send("ALREADY IN GAME")
            return
        r = get_room(self.scope['payload']['id'], self.scope['url_route']['kwargs']['capacity'], self.channel_name, match_id)
        if not r:
            return
        async_to_sync(self.channel_layer.group_add)(r['id'], self.channel_name)

    def disconnect(self, close_code):
        r = find_channels_room(self.scope['payload']['id'], self.channel_name)
        if r:
            async_to_sync(self.channel_layer.group_discard)(r['id'], self.channel_name)
