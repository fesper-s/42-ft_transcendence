from enum import Enum

class RequestStatus(Enum):
    ACCEPTED = 'AC'
    PENDING = 'PN'

    @classmethod
    def choices(cls):
        return [
            (cls.ACCEPTED.value, 'ACCEPTED'),
            (cls.PENDING.value, 'PENDING')
        ]
