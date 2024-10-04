from enum import Enum

class State(Enum):
    PLAYED = "PLY"
    UNPLAYED = "UPL"

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]