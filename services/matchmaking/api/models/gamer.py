from api.enums.status_gamer import ConnectionStatus
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class Gamer(AbstractBaseUser):

    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=50, blank=False, null=False, unique=True)
    username = models.CharField(max_length=20, blank=False, null=False, unique=False)
    name = models.CharField(max_length=50, blank=False, null=False)
    alias_name = models.CharField(max_length=20, blank=False, null=True)
    avatar = models.URLField(blank=False, null=False)
    champions = models.IntegerField(blank=False, null=False, default=0)
    wins = models.IntegerField(blank=False, null=False, default=0)
    losses = models.IntegerField(blank=False, null=False, default=0)
    two_factor = models.BooleanField(default=False)
    status = models.CharField(max_length=2, choices=ConnectionStatus.choices(), default=ConnectionStatus.DISCONNECTED.value)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    def __str__(self):
        return f'Gamer: [ email: {self.email}, username: {self.username} ]'