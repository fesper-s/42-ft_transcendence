from enum import Enum

class Language(Enum):
    C = 'CC'
    CPP = 'CP'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]