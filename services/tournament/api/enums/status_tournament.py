from enum import Enum

class MatchStatus(Enum):
    PENDING = 'PN'
    PROGRESS = 'PR'
    FINISHED = 'FN'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]