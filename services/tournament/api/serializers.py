from rest_framework import serializers
from django.db.models import Q
from api.models.gamer import Gamer
from api.models.gamer_match import GamerMatch
from api.models.gamer_tournament import GamerTournament
from api.models.relationship import Relationship
from api.models.tournament import Tournament
from api.models.match import Match
from api.enums.match_state import State
from api.enums.status_tournament import MatchStatus


class GamerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gamer
        fields = ('id', 'avatar', 'alias_name')


class GamerMatchSerializer(serializers.ModelSerializer):
    gamer = serializers.SerializerMethodField()

    class Meta:
        model = GamerMatch
        fields = ('gamer', 'score')
    
    def get_gamer(self, gamer_match):
        gamer = Gamer.objects.get(id=gamer_match.gamer_id.id)
        serializer = GamerSerializer(gamer)
        return serializer.data


class TournamentSerializer(serializers.ModelSerializer):
    matches = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()
    gamers_count = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = ('id', 'name', 'status', 'round', 'matches', 'creator', 'gamers_count')

    def get_matches(self, tournament):
        matches = Match.objects.filter(tournament=tournament)
        serializer = MatchSerializer(matches, context={"gamer": self.context.get("gamer")}, many=True)
        return serializer.data

    def get_gamers(self, tournament):
        gamers_tournaments = GamerTournament.objects.filter(tournament_id=tournament)
        gamers = []
        for gamer_tournament in gamers_tournaments:
            gamers.append(Gamer.objects.get(id=gamer_tournament.gamer_id.id))
        gamer_data = GamerSerializer(instance=gamers, many=True)
        return gamer_data.data

    def get_gamers_count(self, tournament):
        gamers_tournaments = GamerTournament.objects.filter(tournament_id=tournament)
        return gamers_tournaments.count()

    def is_gamer_in_tournament(self, gamer):
        tournament = Tournament.objects.filter(
            Q(gamertournament__gamer_id=gamer) &
            (Q(status=MatchStatus.PENDING.value) |
            Q(status=MatchStatus.PROGRESS.value))
        ).first()
        return tournament

    def get_creator(self, tournament):
        gamer = self.context.get("gamer")
        return GamerTournament.objects.filter(tournament_id=tournament, gamer_id=gamer, creator=True).exists()

class MatchSerializer(serializers.ModelSerializer):
    gamers = serializers.SerializerMethodField()
    current = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ('id', 'game', 'state', 'round', 'current', 'gamers')

    def get_current(self, match):
        gamer = self.context.get("gamer")
        if match.state == State.PLAYED.value:
            return False
        current_bool = GamerMatch.objects.filter(match_id=match, gamer_id=gamer).exists()
        return current_bool

    def get_gamers(self, match):
        gamer_matches = GamerMatch.objects.filter(match_id=match.id)
        serializer = GamerMatchSerializer(gamer_matches, many=True)
        return serializer.data
