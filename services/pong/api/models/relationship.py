from api.enums.status_relationship import RequestStatus
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class Relationship(models.Model):

    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey('Gamer', on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey('Gamer', on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=2, choices=RequestStatus.choices(), default=RequestStatus.PENDING.value)

    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username}'