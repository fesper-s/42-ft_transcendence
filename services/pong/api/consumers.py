from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from api.models.gamer_match import GamerMatch
from api.models.gamer import Gamer
from api.models.match import Match
from channels.layers import get_channel_layer
import asyncio, random, json
from api.enums.match_state import State

rooms = {}
padd_left = {
    'speed': 30,
    'positionX': 0,
    'positionY': 0,
    'sizeX': 40,
    'sizeY': 200,
    'eliminated': False,
}
padd_right = {
    'speed': 30,
    'positionX': 0,
    'positionY': 0,
    'sizeX': 40,
    'sizeY': 200,
    'eliminated': False,
}
padd_up = {
    'speed': 30,
    'positionX': 0,
    'positionY': 0,
    'sizeX': 200,
    'sizeY': 40,
    'eliminated': False,
}
padd_down = {
    'speed': 30,
    'positionX': 0,
    'positionY': 0,
    'sizeX': 200,
    'sizeY': 40,
    'eliminated': False,
}


async def check_win(room_id, match_id):
    result = None
    match False:
        case elm if elm == rooms[room_id]['padd_left']['info']['eliminated']:
            result = await set_db_four_gamer(room_id, match_id, 'left')
        case elm if elm == rooms[room_id]['padd_right']['info']['eliminated']:
            result = await set_db_four_gamer(room_id, match_id, 'right')
        case elm if elm == rooms[room_id]['padd_up']['info']['eliminated']:
            result = await set_db_four_gamer(room_id, match_id, 'up')
        case elm if elm == rooms[room_id]['padd_down']['info']['eliminated']:
            result = await set_db_four_gamer(room_id, match_id, 'down')
    return result


def walk_over_two(room_id, match_id, pos):
    gamer_left = rooms[room_id]['padd_left']
    gamer_right = rooms[room_id]['padd_right']
    gamer_left_db = Gamer.objects.get(id=gamer_left['user_id'])
    gamer_right_db = Gamer.objects.get(id=gamer_right['user_id'])
    match = get_match(match_id)
    match pos:
        case 'left':
            gamer_match_left, created = GamerMatch.objects.get_or_create(
                match_id=match,
                gamer_id=gamer_left_db,
            )
            gamer_match_left.score = 0
            gamer_match_left.won = False
            gamer_match_right, created = GamerMatch.objects.get_or_create(
                match_id=match,
                gamer_id=gamer_right_db,
            )
            gamer_match_right.score = 2
            gamer_match_right.won = True
            gamer_match_right.save()
            gamer_match_left.save()
            return gamer_left_db.username + ' left you win'
        case 'right':
            gamer_match_left, created = GamerMatch.objects.get_or_create(
                match_id=match,
                gamer_id=gamer_left_db,
            )
            gamer_match_left.score = 2
            gamer_match_left.won = True
            gamer_match_right, created = GamerMatch.objects.get_or_create(
                match_id=match,
                gamer_id=gamer_right_db,
            )
            gamer_match_right.score = 0
            gamer_match_right.won = False
            gamer_match_right.save()
            gamer_match_left.save()
            return gamer_right_db.username + ' left you win'

def eliminate_gamer(padd, room_id):
    if padd['info']['eliminated']:
        return False
    padd['info']['eliminated'] = True
    rooms[room_id]['elimination_count'] += 1
    return True

def walk_over_four(room_id, match_id, pos):
    gamer_left = rooms[room_id]['padd_left']
    gamer_right = rooms[room_id]['padd_right']
    gamer_up = rooms[room_id]['padd_up']
    gamer_down = rooms[room_id]['padd_down']
    match pos:
        case 'left':
            if not eliminate_gamer(gamer_left, room_id):
                return None
        case 'right':
            if not eliminate_gamer(gamer_right, room_id):
                return None
        case 'up':
            if not eliminate_gamer(gamer_up, room_id):
                return None
        case 'down':
            if not eliminate_gamer(gamer_down, room_id):
                return None
    if rooms[room_id]['elimination_count'] >= 3:
        return check_win(room_id, match_id)


@database_sync_to_async
def walk_over(room_id, match_id, pos, capacity):
    try:
        if capacity == 2:
            return walk_over_two(room_id, match_id, pos)
        return walk_over_four(room_id, match_id, pos)
    except Exception as e:
        print(e, flush=True)


def get_match(match_id):
    if not match_id:
        return Match.objects.create(game='PO',
                                    state=State.PLAYED.value)
    match = Match.objects.get(id=match_id)
    match.state = State.PLAYED.value
    match.save()
    return match


@database_sync_to_async
def set_db_four_gamer(room_id, match_id, winner):
    try:
        gamer_left = rooms[room_id]['padd_left']
        gamer_right = rooms[room_id]['padd_right']
        gamer_up = rooms[room_id]['padd_up']
        gamer_down = rooms[room_id]['padd_down']
        match = get_match(match_id)
        gamer_left_db = Gamer.objects.get(id=gamer_left['user_id'])
        gamer_right_db = Gamer.objects.get(id=gamer_right['user_id'])
        gamer_up_db = Gamer.objects.get(id=gamer_up['user_id'])
        gamer_down_db = Gamer.objects.get(id=gamer_down['user_id'])
        result = None
        gamer_match_left, created = GamerMatch.objects.get_or_create(
            match_id=match,
            gamer_id=gamer_left_db
        )
        gamer_match_right, created = GamerMatch.objects.get_or_create(
            match_id=match,
            gamer_id=gamer_right_db
        )
        gamer_match_up, created = GamerMatch.objects.get_or_create(
            match_id=match,
            gamer_id=gamer_up_db
        )
        gamer_match_down, created = GamerMatch.objects.get_or_create(
            match_id=match,
            gamer_id=gamer_down_db
        )
        match winner:
            case 'left':
                gamer_match_left.score = 1
                gamer_match_left.won = True
                gamer_match_right.score = 0
                gamer_match_right.won = False
                gamer_match_up.score = 0
                gamer_match_up.won = False
                gamer_match_down.score = 0
                gamer_match_down.won = False
                gamer_left_db.wins += 1
                gamer_right_db.losses += 1
                gamer_up_db.losses += 1
                gamer_down_db.losses += 1
                result = gamer_left_db.username + ' is the winner'
            case 'right':
                gamer_match_left.score = 0
                gamer_match_left.won = False
                gamer_match_right.score = 1
                gamer_match_right.won = True
                gamer_match_up.score = 0
                gamer_match_up.won = False
                gamer_match_down.score = 0
                gamer_match_down.won = False
                gamer_left_db.losses += 1
                gamer_right_db.wins += 1
                gamer_up_db.losses += 1
                gamer_down_db.losses += 1
                result = gamer_right_db.username + ' is the winner'
            case 'up':
                gamer_match_left.score = 0
                gamer_match_left.won = False
                gamer_match_right.score = 0
                gamer_match_right.won = False
                gamer_match_up.score = 1
                gamer_match_up.won = True
                gamer_match_down.score = 0
                gamer_match_down.won = False
                gamer_left_db.losses += 1
                gamer_right_db.losses += 1
                gamer_up_db.wins += 1
                gamer_down_db.losses += 1
                result = gamer_up_db.username + ' is the winner'
            case 'down':
                gamer_match_left.score = 0
                gamer_match_left.won = False
                gamer_match_right.score = 0
                gamer_match_right.won = False
                gamer_match_up.score = 0
                gamer_match_up.won = False
                gamer_match_down.score = 1
                gamer_match_down.won = True
                gamer_left_db.losses += 1
                gamer_right_db.losses += 1
                gamer_up_db.losses += 1
                gamer_down_db.wins += 1
                result = gamer_down_db.username + ' is the winner'
        gamer_match_left.save()
        gamer_match_right.save()
        gamer_match_up.save()
        gamer_match_down.save()
        gamer_left_db.save()
        gamer_right_db.save()
        gamer_up_db.save()
        gamer_down_db.save()
        return result
    except Exception as e:
        print(e, flush=True)


@database_sync_to_async
def set_db_two_gamer(room_id, match_id):
    gamer_left = rooms[room_id]['padd_left']
    gamer_right = rooms[room_id]['padd_right']
    gamer_left_db = None
    gamer_right_db = None
    match = get_match(match_id)
    try:
        gamer_left_db = Gamer.objects.get(id=gamer_left['user_id'])
        gamer_right_db = Gamer.objects.get(id=gamer_right['user_id'])
        gamer_match_left, created = GamerMatch.objects.get_or_create(
            match_id=match,
            gamer_id=gamer_left_db
        )
        gamer_match_left.score = gamer_left['info']['score']
        gamer_match_left.won = True if gamer_left['info']['score'] == 7 else False
        gamer_match_left.save()
        gamer_match_right, created = GamerMatch.objects.get_or_create(
            match_id=match,
            gamer_id=gamer_right_db
        )
        gamer_match_right.score = gamer_right['info']['score']
        gamer_match_right.won = True if gamer_right['info']['score'] == 7 else False
        gamer_match_right.save()
    except Exception as e:
        print(e, flush=True)
    if gamer_left['info']['score'] == 7:
        gamer_left_db.wins += 1
        gamer_right_db.losses += 1
        gamer_left_db.save()
        gamer_right_db.save()
        return gamer_left_db.username + ' won'
    else:
        gamer_left_db.losses += 1
        gamer_right_db.wins += 1
        gamer_left_db.save()
        gamer_right_db.save()
        return gamer_right_db.username + ' won'


def ball_direction(capacity):
    speed = []
    match capacity:
        case 2:
            speed.append(random.choice([10, -10]))
            speed.append(random.choice([0, -10, 10]))
        case 4:
            speed.append(random.choice([0, -5, 5]))
            speed.append(random.choice([0, -6, 6]))
            if speed[0] == 0 and speed[1] == 0:
                speed[0] = random.choice([-5, 5])
    return speed


class Pong(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        room_id = self.scope['url_route']['kwargs']['room_id']
        self.capacity = self.scope['url_route']['kwargs']['capacity']
        self.match_id = self.scope['url_route']['kwargs'].get('match_id')
        gamer_db = await database_sync_to_async(Gamer.objects.get)(id=self.scope['payload']['id'])
        await self.channel_layer.group_add(
            room_id,
            self.channel_name
        )
        if room_id not in rooms:
            rooms[room_id] = {
                'padd_left': {
                    'gamer': self.channel_name,
                    'user_id': self.scope['payload']['id'],
                    'info': padd_left.copy(),
                    'username': gamer_db.username,
                    'avatar': gamer_db.avatar
                },
            }
            await self.send('1')
        else:
            if rooms[room_id].get('padd_right') is None and self.capacity >= 2:
                rooms[room_id]['padd_right'] = {
                    'gamer': self.channel_name,
                    'user_id': self.scope['payload']['id'],
                    'info': padd_right.copy(),
                    'username': gamer_db.username,
                    'avatar': gamer_db.avatar
                }
                await self.send('2')
            elif rooms[room_id].get('padd_up') is None and self.capacity > 2:
                rooms[room_id]['padd_up'] = {
                    'gamer': self.channel_name,
                    'user_id': self.scope['payload']['id'],
                    'info': padd_up.copy(),
                    'username': gamer_db.username,
                    'avatar': gamer_db.avatar
                }
                await self.send('3')
            elif rooms[room_id].get('padd_down') is None and self.capacity > 2:
                rooms[room_id]['padd_down'] = {
                    'gamer': self.channel_name,
                    'user_id': self.scope['payload']['id'],
                    'info': padd_down.copy(),
                    'username': gamer_db.username,
                    'avatar': gamer_db.avatar
                }
                await self.send('4')
            if len(rooms[room_id]) == self.capacity:
                await self.start_game(room_id)

    async def pong_message(self, event):
        if (event['message'] == 'ball'
                and self.scope['url_route']['kwargs']['room_id'] in rooms):
            await self.send(text_data=json.dumps(
                rooms[self.scope['url_route']['kwargs']['room_id']]
            ))
        else:
            await self.send(text_data=json.dumps(
                event['message']
            ))

    async def disconnect(self, close_code):
        room_id = self.scope['url_route']['kwargs']['room_id']
        message = None
        await self.channel_layer.group_discard(
            room_id,
            self.channel_name
        )
        if room_id in rooms:
            match self.channel_name:
                case gamer if gamer == rooms[room_id]['padd_left']['gamer']:
                    if close_code is not None:
                        message = await walk_over(room_id, self.match_id, 'left', self.capacity)
                case gamer if gamer == rooms[room_id]['padd_right']['gamer']:
                    if close_code is not None:
                        message = await walk_over(room_id, self.match_id, 'right', self.capacity)
                case gamer if gamer == rooms[room_id]['padd_up']['gamer']:
                    if close_code is not None:
                        message = await walk_over(room_id, self.match_id, 'up', self.capacity)
                case gamer if gamer == rooms[room_id]['padd_down']['gamer']:
                    if close_code is not None:
                        message = await walk_over(room_id, self.match_id, 'down', self.capacity)
            if message is not None:
                await self.channel_layer.group_send(
                    room_id,
                    {
                        'type': 'pong.message',
                        'message': message
                    }
                )
                del rooms[room_id]
            if self.capacity == 2 and room_id in rooms:
                del rooms[room_id]

    async def receive(self, text_data=None, bytes_data=None):
        room_id = self.scope['url_route']['kwargs']['room_id']
        recieved = False
        match text_data:
            case 'up' | 'w':
                recieved = True
                if self.channel_name in rooms[room_id]['padd_left']['gamer']:
                    rooms[room_id]['padd_left']['info']['positionY'] -= rooms[room_id]['padd_left']['info']['speed']
                elif self.channel_name in rooms[room_id]['padd_right']['gamer']:
                    rooms[room_id]['padd_right']['info']['positionY'] -= rooms[room_id]['padd_right']['info']['speed']
            case 'down' | 's':
                recieved = True
                if self.channel_name in rooms[room_id]['padd_left']['gamer']:
                    rooms[room_id]['padd_left']['info']['positionY'] += rooms[room_id]['padd_left']['info']['speed']
                elif self.channel_name in rooms[room_id]['padd_right']['gamer']:
                    rooms[room_id]['padd_right']['info']['positionY'] += rooms[room_id]['padd_right']['info']['speed']
        if self.capacity == 4 and not recieved:
            match text_data:
                case 'left' | 'a':
                    if self.channel_name in rooms[room_id]['padd_up']['gamer']:
                        rooms[room_id]['padd_up']['info']['positionX'] -= rooms[room_id]['padd_up']['info']['speed']
                    elif self.channel_name in rooms[room_id]['padd_down']['gamer']:
                        rooms[room_id]['padd_down']['info']['positionX'] -= rooms[room_id]['padd_down']['info']['speed']
                case 'right' | 'd':
                    if self.channel_name in rooms[room_id]['padd_up']['gamer']:
                        rooms[room_id]['padd_up']['info']['positionX'] += rooms[room_id]['padd_up']['info']['speed']
                    elif self.channel_name in rooms[room_id]['padd_down']['gamer']:
                        rooms[room_id]['padd_down']['info']['positionX'] += rooms[room_id]['padd_down']['info']['speed']
        await self.paddleCollision(room_id)

    async def start_game(self, room_id):
        self.init_game(room_id)
        rooms[room_id]['ball']['positionX'] += rooms[room_id]['ball']['speedX']
        rooms[room_id]['ball']['positionY'] += rooms[room_id]['ball']['speedY']
        await self.channel_layer.group_send(
            room_id,
            {
                'type': 'pong.message',
                'message': 'ball',
            }
        )
        if room_id in rooms:
            asyncio.create_task(self.game_loop(room_id))

    def init_game(self, room_id):
        rooms[room_id]['padd_left']['info']['score'] = 0
        rooms[room_id]['padd_right']['info']['score'] = 0
        if self.capacity == 4:
            rooms[room_id]['canvas_width'] = 1300
            rooms[room_id]['canvas_height'] = 1300
            rooms[room_id]['padd_up']['info']['score'] = 0
            rooms[room_id]['padd_up']['info']['positionX'] = rooms[room_id]['canvas_width'] / 2 - 100
            rooms[room_id]['padd_up']['info']['positionY'] = 100
            rooms[room_id]['padd_down']['info']['score'] = 0
            rooms[room_id]['padd_down']['info']['positionX'] = rooms[room_id]['canvas_width'] / 2 - 100
            rooms[room_id]['padd_down']['info']['positionY'] = rooms[room_id]['canvas_height'] - 100
            rooms[room_id]['elimination_count'] = 0
        else:
            rooms[room_id]['canvas_width'] = 1920
            rooms[room_id]['canvas_height'] = 1080
        rooms[room_id]['padd_left']['info']['positionX'] = 60
        rooms[room_id]['padd_left']['info']['positionY'] = rooms[room_id]['canvas_height'] / 2 - 100
        rooms[room_id]['padd_right']['info']['positionX'] = rooms[room_id]['canvas_width'] - 100
        rooms[room_id]['padd_right']['info']['positionY'] = rooms[room_id]['canvas_height'] / 2 - 100
        speed = ball_direction(self.capacity)
        rooms[room_id]['ball'] = {
            'speedX': speed[0],
            'speedY': speed[1],
            'positionX': rooms[room_id]['canvas_width'] / 2,
            'positionY': rooms[room_id]['canvas_height'] / 2,
            'size': 20,
        }

    async def reset_game(self, room_id, x):
        speed = ball_direction(self.capacity)
        if x and rooms[room_id]['ball']['speedX'] > 0:
            if self.capacity == 4:
                rooms[room_id]['padd_right']['info']['eliminated'] = True
                rooms[room_id]['elimination_count'] += 1
            else:
                rooms[room_id]['padd_left']['info']['score'] += 1
                if rooms[room_id]['padd_left']['info']['score'] == 7:
                    result = await set_db_two_gamer(room_id, self.match_id)
                    await self.channel_layer.group_send(
                        room_id,
                        {
                            'type': 'pong.message',
                            'message': result
                        }
                    )
            rooms[room_id]['ball']['speedX'] = 10
        elif x:
            if self.capacity == 4:
                rooms[room_id]['padd_left']['info']['eliminated'] = True
                rooms[room_id]['elimination_count'] += 1
            else:
                rooms[room_id]['padd_right']['info']['score'] += 1
                if rooms[room_id]['padd_right']['info']['score'] == 7:
                    result = await set_db_two_gamer(room_id, self.match_id)
                    await self.channel_layer.group_send(
                        room_id,
                        {
                            'type': 'pong.message',
                            'message': result
                        }
                    )
            rooms[room_id]['ball']['speedX'] = -10
        elif not x:
            if rooms[room_id]['ball']['speedY'] > 0:
                rooms[room_id]['padd_down']['info']['eliminated'] = True
            else:
                rooms[room_id]['padd_up']['info']['eliminated'] = True
            rooms[room_id]['elimination_count'] += 1
            rooms[room_id]['ball']['speedX'] = speed[0]
        rooms[room_id]['ball']['speedY'] = speed[1]
        rooms[room_id]['ball']['positionX'] = rooms[room_id]['canvas_width'] / 2
        rooms[room_id]['ball']['positionY'] = rooms[room_id]['canvas_height'] / 2
        rooms[room_id]['padd_left']['info']['positionY'] = rooms[room_id]['canvas_height'] / 2 - 100
        rooms[room_id]['padd_right']['info']['positionY'] = rooms[room_id]['canvas_height'] / 2 - 100
        if self.capacity == 4:
            rooms[room_id]['padd_up']['info']['positionX'] = rooms[room_id]['canvas_width'] / 2 - 100
            rooms[room_id]['padd_down']['info']['positionX'] = rooms[room_id]['canvas_width'] / 2 - 100

    async def BallCollision(self, room_id):
        if (rooms[room_id]['ball']['positionX'] +
                rooms[room_id]['ball']['size'] >= rooms[room_id]['canvas_width']):
            if rooms[room_id]['padd_right']['info']['eliminated']:
                rooms[room_id]['ball']['speedX'] *= -1
            else:
                await self.reset_game(room_id, True)
        if (rooms[room_id]['ball']['positionX'] -
                rooms[room_id]['ball']['size'] <= 0):
            if rooms[room_id]['padd_left']['info']['eliminated']:
                rooms[room_id]['ball']['speedX'] *= -1
            else:
                await self.reset_game(room_id, True)
        if (rooms[room_id]['ball']['positionY'] +
                rooms[room_id]['ball']['size'] >= rooms[room_id]['canvas_height']):
            if self.capacity == 4 and not rooms[room_id]['padd_down']['info']['eliminated']:
                await self.reset_game(room_id, False)
            else:
                rooms[room_id]['ball']['speedY'] *= -1
        if rooms[room_id]['ball']['positionY'] - rooms[room_id]['ball']['size'] <= 0:
            if self.capacity == 4 and not rooms[room_id]['padd_up']['info']['eliminated']:
                await self.reset_game(room_id, False)
            else:
                rooms[room_id]['ball']['speedY'] *= -1

    def get_padd_center(self, room_id, side):
        size_x = rooms[room_id]['padd_left']['info']['sizeX']
        size_y = rooms[room_id]['padd_left']['info']['sizeY']
        match side:
            case 'leftX':
                return rooms[room_id]['padd_left']['info']['positionX'] + size_x / 2
            case 'leftY':
                return rooms[room_id]['padd_left']['info']['positionY'] + size_y / 2
            case 'rightX':
                return rooms[room_id]['padd_right']['info']['positionX'] + size_x / 2
            case 'rightY':
                return rooms[room_id]['padd_right']['info']['positionY'] + size_y / 2
        tmp = size_x
        size_x = size_y
        size_y = tmp
        match side:
            case 'upX':
                return rooms[room_id]['padd_up']['info']['positionX'] + size_x / 2
            case 'upY':
                return rooms[room_id]['padd_up']['info']['positionY'] - size_y / 2
            case 'downX':
                return rooms[room_id]['padd_down']['info']['positionX'] + size_x / 2
            case 'downY':
                return rooms[room_id]['padd_down']['info']['positionY'] + size_y / 2

    async def BallPaddleCollision(self, room_id):
        ball_size = rooms[room_id]['ball']['size']
        sizeY = rooms[room_id]['padd_left']['info']['sizeY']
        sizeX = rooms[room_id]['padd_left']['info']['sizeX']
        leftX_center = self.get_padd_center(room_id, 'leftX')
        leftY_center = self.get_padd_center(room_id, 'leftY')
        rightX_center = self.get_padd_center(room_id, 'rightX')
        rightY_center = self.get_padd_center(room_id, 'rightY')
        left_dx = abs(rooms[room_id]['ball']['positionX'] - leftX_center)
        left_dy = abs(rooms[room_id]['ball']['positionY'] - leftY_center)
        right_dx = abs(rooms[room_id]['ball']['positionX'] - rightX_center)
        right_dy = abs(rooms[room_id]['ball']['positionY'] - rightY_center)
        if (not rooms[room_id]['padd_left']['info']['eliminated'] and
                (left_dx <= ball_size + sizeX / 2 and
                    left_dy <= ball_size + sizeY / 2)):
            if (rooms[room_id]['ball']['positionX'] >=
                leftX_center and rooms[room_id]['ball']['speedX'] > 0) or (
                    rooms[room_id]['ball']['positionX'] <=
                    leftX_center and rooms[room_id]['ball']['speedX'] < 0):
                return
            rooms[room_id]['ball']['speedX'] *= -1
        elif (not rooms[room_id]['padd_right']['info']['eliminated'] and
              (right_dx <= ball_size + sizeX / 2 and
                right_dy <= ball_size + sizeY / 2)):
            if (rooms[room_id]['ball']['positionX'] >=
                rightX_center and rooms[room_id]['ball']['speedX'] > 0) or (
                    rooms[room_id]['ball']['positionX'] <=
                    rightX_center and rooms[room_id]['ball']['speedX'] < 0):
                return
            rooms[room_id]['ball']['speedX'] *= -1
        if self.capacity == 4:
            tmp = sizeX
            sizeX = sizeY
            sizeY = tmp
            upX_center = self.get_padd_center(room_id, 'upX')
            upY_center = self.get_padd_center(room_id, 'upY')
            downX_center = self.get_padd_center(room_id, 'downX')
            downY_center = self.get_padd_center(room_id, 'downY')
            up_dx = abs(rooms[room_id]['ball']['positionX'] - upX_center)
            up_dy = abs(rooms[room_id]['ball']['positionY'] - upY_center)
            down_dx = abs(rooms[room_id]['ball']['positionX'] - downX_center)
            down_dy = abs(rooms[room_id]['ball']['positionY'] - downY_center)
            if (not rooms[room_id]['padd_up']['info']['eliminated'] and
                (up_dx <= ball_size + sizeX / 2 and
                    up_dy <= ball_size + sizeY / 2)):
                if (rooms[room_id]['ball']['positionY'] >=
                    upY_center and rooms[room_id]['ball']['speedY'] > 0) or (
                        rooms[room_id]['ball']['positionY'] <=
                        upY_center and rooms[room_id]['ball']['speedY'] < 0):
                    return
                rooms[room_id]['ball']['speedY'] *= -1
            elif (not rooms[room_id]['padd_down']['info']['eliminated'] and
                  (down_dx <= ball_size + sizeX / 2 and
                    down_dy <= ball_size + sizeY / 2)):
                if (rooms[room_id]['ball']['positionY'] >=
                    downY_center and rooms[room_id]['ball']['speedY'] > 0) or (
                        rooms[room_id]['ball']['positionY'] <=
                        downY_center and rooms[room_id]['ball']['speedY'] < 0):
                    return
                rooms[room_id]['ball']['speedY'] *= -1

    async def paddleCollision(self, room_id):
        size = rooms[room_id]['padd_right']['info']['sizeY']
        pos_right = rooms[room_id]['padd_right']['info']['positionY']
        pos_left = rooms[room_id]['padd_left']['info']['positionY']
        if not rooms[room_id]['padd_right']['info']['eliminated']:
            if pos_right + size >= rooms[room_id]['canvas_height']:
                rooms[room_id]['padd_right']['info']['positionY'] \
                    = rooms[room_id]['canvas_height'] - size
            elif pos_right <= 0:
                rooms[room_id]['padd_right']['info']['positionY'] = 0
        if not rooms[room_id]['padd_left']['info']['eliminated']:
            if pos_left + size >= rooms[room_id]['canvas_height']:
                rooms[room_id]['padd_left']['info']['positionY'] \
                    = rooms[room_id]['canvas_height'] - size
            elif pos_left <= 0:
                rooms[room_id]['padd_left']['info']['positionY'] = 0
        if self.capacity == 4:
            size = rooms[room_id]['padd_up']['info']['sizeX']
            pos_up = rooms[room_id]['padd_up']['info']['positionX']
            pos_down = rooms[room_id]['padd_down']['info']['positionX']
            if not rooms[room_id]['padd_up']['info']['eliminated']:
                if pos_up + size >= rooms[room_id]['canvas_width']:
                    rooms[room_id]['padd_up']['info']['positionX'] \
                        = rooms[room_id]['canvas_width'] - size
                elif pos_up <= 0:
                    rooms[room_id]['padd_up']['info']['positionX'] = 0
            if not rooms[room_id]['padd_down']['info']['eliminated']:
                if pos_down + size >= rooms[room_id]['canvas_width']:
                    rooms[room_id]['padd_down']['info']['positionX'] \
                        = rooms[room_id]['canvas_width'] - size
                elif pos_down <= 0:
                    rooms[room_id]['padd_down']['info']['positionX'] = 0

    async def game_loop(self, room_id):
        await asyncio.sleep(2)
        while True:
            if room_id not in rooms:
                print('Game over for: ', room_id)
                break
            rooms[room_id]['ball']['positionX'] += rooms[room_id]['ball']['speedX']
            rooms[room_id]['ball']['positionY'] += rooms[room_id]['ball']['speedY']
            try:
                await self.BallCollision(room_id)
                await self.paddleCollision(room_id)
                await self.BallPaddleCollision(room_id)
                if self.capacity == 4 and rooms[room_id]['elimination_count'] > 2:
                    result = await check_win(room_id, self.match_id)
                    await self.channel_layer.group_send(
                        room_id,
                        {
                            'type': 'pong.message',
                            'message': result
                        }
                    )
                    return
                await self.channel_layer.group_send(
                    room_id,
                    {
                        'type': 'pong.message',
                        'message': 'ball',
                    }
                )
            except Exception as e:
                print(e, flush=True)
            if rooms[room_id]['ball']['speedX'] > 0:
                rooms[room_id]['ball']['speedX'] += 0.01
            else:
                rooms[room_id]['ball']['speedX'] -= 0.01
            if rooms[room_id]['ball']['speedY'] > 0:
                rooms[room_id]['ball']['speedY'] += 0.01
            else:
                rooms[room_id]['ball']['speedY'] -= 0.01
            await asyncio.sleep(0.015)
