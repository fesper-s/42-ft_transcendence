from api.models.gamer import Gamer
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class GamerTournament(models.Model):
    id = models.AutoField(primary_key=True)
    gamer_id = models.ForeignKey(Gamer, on_delete=models.CASCADE, null=False, blank=False)
    tournament_id = models.ForeignKey('Tournament', on_delete=models.CASCADE, null=False, blank=False)
    creator = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return f'{self.gamer_id} -> {self.creator}'
