from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from api.models import Gamer
from api.enums import ConnectionStatus

gamersOpenTabs = {}

@database_sync_to_async
def set_gamer_status(gamer,  gamerStatus):
    gamer.status = gamerStatus
    gamer.save(update_fields=["status"])


class LoginConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.id = None
        if self.scope['status'] == 'Valid':
            self.gamer = self.scope['gamer']
            self.id = self.gamer.id
            if self.id not in gamersOpenTabs:
                await set_gamer_status(self.gamer, ConnectionStatus.CONNECTED.value)
                gamersOpenTabs[self.id] = 1
            else:
                gamersOpenTabs[self.id] += 1
        await self.send(self.scope['status'])

    async def disconnect(self, close_code):
        if self.id is None:
            return
        if gamersOpenTabs[self.id] == 1:
            await set_gamer_status(self.gamer, ConnectionStatus.DISCONNECTED.value)
            del gamersOpenTabs[self.id]
        else:
            gamersOpenTabs[self.id] -= 1

    async def receive(self, text_data):
        pass
