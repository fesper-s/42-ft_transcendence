from enum import Enum

class Game(Enum):
    PONG = "PO"

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]
