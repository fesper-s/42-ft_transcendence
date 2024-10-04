from rest_framework import serializers
from .models import Gamer


class GamerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gamer
        fields = '__all__'

class GamerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gamer
        fields = ['id', 'username', 'email', 'name', 'avatar', 'status', 'alias_name', 'two_factor', 'champions', 'wins', 'losses']
