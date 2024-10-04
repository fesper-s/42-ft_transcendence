from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from api.enums.match_state import State
from api.enums.match_game import Game
from api.models.gamer import Gamer
from enum import Enum


class Match(models.Model):
    class Game(Enum):
        PONG = "PO"

        @classmethod
        def choices(cls):
            return [(choice.value, choice.name) for choice in cls]

    class State(Enum):
        PLAYED = "PLY"
        UNPLAYED = "UPL"

        @classmethod
        def choices(cls):
            return [(choice.value, choice.name) for choice in cls]

    id = models.AutoField(primary_key=True)
    game = models.CharField(
        max_length=2,
        choices=Game.choices(),
        null=False,
        blank=False,
        default=Game.PONG.value,
    )
    tournament = models.ForeignKey(
        "Tournament", on_delete=models.CASCADE, null=True, blank=False
    )
    round = models.IntegerField(default=1)
    state = models.CharField(
        max_length=3,
        choices=State.choices(),
        null=False,
        blank=False,
        default=State.UNPLAYED.value,
    )
