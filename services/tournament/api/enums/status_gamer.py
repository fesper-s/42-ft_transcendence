from enum import Enum

class ConnectionStatus(Enum):
    CONNECTED = 'CN'
    DISCONNECTED = 'DC'
    PLAYING = 'PL'

    @classmethod
    def choices(cls):
        return [
            (cls.CONNECTED.value, 'CONNECTED'),
            (cls.DISCONNECTED.value, 'DISCONNECTED'),
            (cls.PLAYING.value, 'PLAYING')
        ]
