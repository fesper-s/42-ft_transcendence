from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models.gamer import Gamer
from api.models.gamer_match import GamerMatch
from api.models.gamer_tournament import GamerTournament
from api.models.relationship import Relationship
from api.models.tournament import Tournament
from api.models.match import Match
from .serializers import TournamentSerializer
from .settings import COMPETITORS, ROUNDS
from .decorators import jwt_cookie_required
from itertools import cycle

from api.enums.status_tournament import MatchStatus
from api.enums.match_state import State


def update_tournament(tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    if tournament.status == MatchStatus.FINISHED.value:
        return
    current_round = tournament.round
    current_round_matches = Match.objects.filter(tournament=tournament, round=current_round)
    if all(match.state == State.PLAYED.value for match in current_round_matches):
        if tournament.round == 3:
            tournament.status = MatchStatus.FINISHED.value
            winner = GamerMatch.objects.get(match_id__in=current_round_matches, won=True)
            winner.gamer_id.champions += 1
            tournament.save()
            winner.gamer_id.save()
            return
        winning_gamers = list(GamerMatch.objects.filter(match_id__in=current_round_matches, won=True))
        if winning_gamers:
            tournament.round += 1
            tournament.save()
        while len(winning_gamers) >= 2:
            gamer1_match = winning_gamers.pop(0)
            gamer2_match = winning_gamers.pop(0)
            gamer1 = gamer1_match.gamer_id
            gamer2 = gamer2_match.gamer_id
            tournament_match = Match.objects.create(
                tournament=tournament,
                game="PO",
                round=current_round + 1
            )
            GamerMatch.objects.create(
                match_id=tournament_match,
                gamer_id=gamer1
            )
            GamerMatch.objects.create(
                match_id=tournament_match,
                gamer_id=gamer2
            )


class TournamentView(APIView):

    @method_decorator(jwt_cookie_required)
    def get(self, request):
        gamer_id = request.decoded_token['id']
        serializer = TournamentSerializer()
        gamer = Gamer.objects.get(id=gamer_id)
        if serializer.is_gamer_in_tournament(gamer):
            try:
                tournament = serializer.is_gamer_in_tournament(gamer)
                serializer = TournamentSerializer(tournament, context={"gamer": gamer})
                if tournament.status == MatchStatus.PENDING.value:
                    return Response({"statusCode": 200, "current_tournament": serializer.data, "gamers": serializer.get_gamers(tournament)})
                update_tournament(tournament.id)
                return Response({"statusCode": 200, "current_tournament": serializer.data})
            except Tournament.DoesNotExist:
                return Response({"statusCode": 404, "message": "Tournament not found"})
        tournaments = Tournament.objects.filter(status='PN')
        gamer_finished_tournament = GamerTournament.objects.filter(gamer_id=gamer).order_by('-id').first()
        response_data = {}
        if gamer_finished_tournament is not None:
            finished_tournament = Tournament.objects.filter(id=gamer_finished_tournament.tournament_id.id).first()
            serializer_finished = TournamentSerializer(finished_tournament)
            response_data["current_tournament"] = serializer_finished.data
        if not tournaments:
            response_data.update({"statusCode": 404, "message": "No Tournaments are available"})
            return Response(response_data)
        serializer_all = TournamentSerializer(tournaments, many=True)
        response_data.update({"statusCode": 200, "tournaments": serializer_all.data})
        return Response(response_data)

    @method_decorator(jwt_cookie_required)
    def post(self, request):
        action = request.data.get('action')
        tournament_id = request.data.get('tournament_id')
        name = request.data.get('tournament_name')
        alias = request.data.get('alias_name')
        gamer_id = request.decoded_token['id']
        try:
            gamer = Gamer.objects.get(id=gamer_id)
        except Gamer.DoesNotExist:
            return Response({"statusCode": 400, "message": "Gamer does not exist"})
        if "create" in action:
            if name is None or len(name) == 0 or alias is None or len(alias) == 0:
                return Response({"statusCode": 400, "message": "Invalid Tournament name"})
            serializer = TournamentSerializer()
            if serializer.is_gamer_in_tournament(gamer):
                return Response({"statusCode": 400, "message": "Already in a Tournament"})
            tournament = Tournament.objects.create(name=name)
            GamerTournament.objects.create(gamer_id=gamer, tournament_id=tournament, creator=True)
            serializer = TournamentSerializer(tournament)
            gamer.alias_name = alias
            gamer.save()
            return Response({"statusCode": 200, "current_tournament": serializer.get_gamers(tournament)}, status=201)
        try:
            tournament = Tournament.objects.get(id=tournament_id)
            serializer = TournamentSerializer(tournament)
        except Tournament.DoesNotExist:
            return Response({"statusCode": 404, "message": "Not found"})
        if "join" in action:
            if tournament_id is None or len(tournament_id) == 0 or alias is None or len(alias) == 0:
                return Response({"statusCode": 400, "message": "Missing Tournament id"})
            if tournament.status == 'PN' and serializer.get_gamers_count(tournament) < COMPETITORS:
                if serializer.is_gamer_in_tournament(gamer):
                    return Response({"statusCode": 400, "message": "Already in a Tournament"})
                gamer.alias_name = alias
                gamer.save()
                GamerTournament.objects.create(gamer_id=gamer, tournament_id=tournament)
                return Response({"statusCode": 200, "message": "Successfully joined tournament"})
            return Response({"statusCode": 400, "message": "Tournament is full"})
        elif "leave" in action:
            if tournament.status != MatchStatus.PENDING.value:
                return Response({"statusCode": 400, "message": "Tournament status is not pending"})
            try:
                gamer_tournament = GamerTournament.objects.get(gamer_id=gamer, tournament_id=tournament)
            except GamerTournament.DoesNotExist:
                return Response({"statusCode": 400, "message": "Gamer is not in the Tournament"})
            if gamer_tournament.creator:
                tournament.delete()
                return Response({"statusCode": 200, "message": "Tournament deleted along with gamer"})
            else:
                gamer_tournament.delete()
                return Response({"statusCode": 200, "message": "Gamer removed from Tournament"})
        elif "start" in action:
            if not GamerTournament.objects.filter(gamer_id=gamer, tournament_id=tournament, creator=True).exists():
                return Response({"statusCode": 400, "message": "Tournament cannot be started"})
            if serializer.get_gamers_count(tournament) != COMPETITORS:
                return Response({"statusCode": 400, "message": "Tournament not full yet"})
            if tournament.status == MatchStatus.PENDING.value:
                gamers_tournaments = GamerTournament.objects.filter(tournament_id=tournament)
                gamers_cycle = cycle(gamers_tournaments)
                for i in range(0, COMPETITORS - 1, 2):
                    gamer1 = next(gamers_cycle).gamer_id
                    gamer2 = next(gamers_cycle).gamer_id
                    tournament_match = Match.objects.create(
                        tournament=tournament,
                        game="PO",
                        round=tournament.round
                    )
                    GamerMatch.objects.create(
                        match_id=tournament_match,
                        gamer_id=gamer1
                    )
                    GamerMatch.objects.create(
                        match_id=tournament_match,
                        gamer_id=gamer2
                    )
                tournament.status = MatchStatus.PROGRESS.value
                tournament.save()
                return Response({"statusCode": 200, "message": "Tournament started",
                                 "tournament_id": tournament_id})
            return Response({"statusCode": 400, "message": "Tournament is not pending"})
        return Response({"statusCode": 400, "message": "Wrong Action"})
