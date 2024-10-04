from django.core.cache import cache
import re
import jwt
from django.db import close_old_connections
from channels.auth import AuthMiddlewareStack
from .settings import SECRET_KEY
from .models import Gamer
from channels.db import database_sync_to_async


@database_sync_to_async
def get_gamer_by_id(id):
    return Gamer.objects.get(id=id)

class TokenMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        close_old_connections()
        headers = dict(scope["headers"])
        if b"cookie" in headers:
            cookies = headers[b"cookie"].decode()
            match = re.search("jwt_token=(.*)", cookies)
            if match is not None:
                token_key = match.group(1)
                await self.decode_token(token_key, scope)
                return await self.inner(scope, receive, send)
        scope['status'] = "Invalid"
        return await self.inner(scope, receive, send)

    async def decode_token(self, token_key, scope):
        try:
            payload = jwt.decode(token_key, SECRET_KEY, algorithms=['HS256'])
            if (payload['twofa']):
                scope['status'] = "Twofa"
                return
            scope['gamer'] = await get_gamer_by_id(payload['id'])
            scope['status'] = "Valid"
        except (Gamer.DoesNotExist, jwt.InvalidTokenError):
            scope['status'] = "Invalid"

MyAuthMiddlewareStack = lambda inner: TokenMiddleware(AuthMiddlewareStack(inner))
