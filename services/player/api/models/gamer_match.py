from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from api.enums.language_gamer_match import Language
from api.models.gamer import Gamer
from api.models.match import Match


class GamerMatch(models.Model):
    id = models.AutoField(primary_key=True)
    match_id = models.ForeignKey('Match', on_delete=models.CASCADE, null=False, blank=False)
    gamer_id = models.ForeignKey(Gamer, on_delete=models.CASCADE, null=False, blank=False)
    score = models.IntegerField(default=0, null=False, blank=False)
    language = models.CharField(max_length=2, choices=Language.choices(), null=True, blank=False, default=Language.C.value)
    executable_path = models.CharField(max_length=255, null=True, blank=False)
    won = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return f"Score: {self.score}"