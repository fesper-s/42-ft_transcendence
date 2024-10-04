from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from api.enums.status_tournament import MatchStatus


class Tournament(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, blank=False, null=False, unique=False)
    round = models.IntegerField(default=1)
    status = models.CharField(max_length=2,
                              choices=MatchStatus.choices(),
                              default=MatchStatus.PENDING.value,
                              null=False, blank=False)

    def __str__(self):
        return f"Tournament : {self.id}"