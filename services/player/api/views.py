from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import GamerInfoSerializer
from api.models.gamer import Gamer
from api.models.gamer_match import GamerMatch
from api.models.gamer_tournament import GamerTournament
from api.models.relationship import Relationship
from api.models.tournament import Tournament

from .decorators import jwt_cookie_required
import urllib.parse
import os
from django.db.models import Q


class GamerInfo(APIView):

    @method_decorator(jwt_cookie_required)
    def get(self, request):
        try:
            print(request.decoded_token["id"])
            username = request.query_params.get("username")
            if username:
                gamer = Gamer.objects.filter(username=username)
                if not gamer.exists():
                    raise Gamer.DoesNotExist
                serializer = GamerInfoSerializer(gamer, many=True)
                return Response(
                    {
                        "status": 200,
                        "gamers": serializer.data,
                        "message": "User found successfully",
                    }
                )
            gamer = Gamer.objects.get(id=request.decoded_token["id"])
            serializer = GamerInfoSerializer(gamer)
            return Response({"status": 200, "gamer": serializer.data})
        except Gamer.DoesNotExist:
            return Response(
                {
                    "status": 404,
                    "message": "User not found",
                }
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": str(e),
                }
            )

    @method_decorator(jwt_cookie_required)
    def post(self, request):
        try:
            changed = False
            id = request.decoded_token["id"]
            gamer_data = request.data.get("gamer")
            gamer = Gamer.objects.get(id=id)
            if "username" in gamer_data:
                username = " ".join(gamer_data["username"].split())
                if not username or len(gamer_data["username"]) > 8:
                    return Response(
                        {
                            "status": 400,
                            "message": "Invalid username",
                        }
                    )
                gamer.username = username
                changed = True
            if "name" in gamer_data:
                name = " ".join(gamer_data["name"].split())
                if not name or len(name) > 20:
                    return Response(
                        {
                            "status": 400,
                            "message": "Invali first name",
                        }
                    )
                gamer.name = name
                changed = True
            if "two_factor" in gamer_data and gamer_data["two_factor"] is False:
                gamer.two_factor = gamer_data["two_factor"]
                changed = True
            gamer.save()
            message = "User updated successfully" if changed else "No changes detected"
            return Response(
                {
                    "status": 200,
                    "message": message,
                }
            )
        except Gamer.DoesNotExist:
            return Response(
                {
                    "status": 404,
                    "message": "User not found",
                }
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": str(e),
                }
            )


class GamerAvatarUpload(APIView):

    @method_decorator(jwt_cookie_required)
    def post(self, request):
        try:
            id = request.decoded_token["id"]
            file = request.FILES["avatar"]
            file_path = os.path.join(settings.MEDIA_ROOT, file.name)
            default_storage.save(file_path, ContentFile(file.read()))
            file_url = urllib.parse.urljoin(
                settings.PUBLIC_PLAYER_URL, os.path.join(settings.MEDIA_URL, file.name)
            )
            gamer = Gamer.objects.get(id=id)
            gamer.avatar = file_url
            gamer.save()
            return Response(
                {
                    "status": 200,
                    "message": "Avatar updated successfully",
                }
            )
        except Gamer.DoesNotExist:
            return Response(
                {
                    "status": 404,
                    "message": "User not found",
                }
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": str(e),
                }
            )


class GamerFriendship(APIView):

    @method_decorator(jwt_cookie_required)
    def get(self, request):
        id = request.decoded_token["id"]
        try:
            get_type = request.query_params.get("target")
            if get_type == "invites":
                friendships = Relationship.objects.filter(receiver=id, status="PN")
                friendship_data = []
                for friendship in friendships:
                    friend = friendship.sender
                    friend_data = GamerInfoSerializer(friend).data
                    friendship_data.append(friend_data)
                return Response({"status": 200, "friendships": friendship_data})
            elif get_type == "friends":
                friendships = Relationship.objects.filter(
                    Q(sender=id) | Q(receiver=id), status="AC"
                )
                friendship_data = []
                for friendship in friendships:
                    friend = (
                        friendship.sender
                        if friendship.sender.id != id
                        else friendship.receiver
                    )
                    friend_data = GamerInfoSerializer(friend).data
                    friendship_data.append(friend_data)
                return Response({"status": 200, "friendships": friendship_data})
            elif get_type == "requests":
                friendships = Relationship.objects.filter(sender=id, status="PN")
                friendship_data = []
                for friendship in friendships:
                    friend = friendship.receiver
                    friend_data = GamerInfoSerializer(friend).data
                    friendship_data.append(friend_data)
                return Response({"status": 200, "friendships": friendship_data})
            else:
                return Response(
                    {
                        "status": 400,
                        "message": "Invalid request",
                    }
                )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": str(e),
                }
            )

    @method_decorator(jwt_cookie_required)
    def post(self, request):
        id = request.decoded_token["id"]
        try:
            sender = Gamer.objects.get(id=id)
            receiver_id = request.data.get("target_id")
            if receiver_id == id:
                return Response(
                    {
                        "status": 400,
                        "message": "You can't send a friend request to yourself",
                    }
                )
            receiver = Gamer.objects.get(id=receiver_id)
            if Relationship.objects.filter(sender=sender, receiver=receiver).exists():
                return Response(
                    {
                        "status": 400,
                        "message": "Friend request already sent",
                    }
                )
            elif Relationship.objects.filter(sender=receiver, receiver=sender).exists():
                friendships = Relationship.objects.filter(
                    sender=receiver, receiver=sender
                )
                friendships.update(status="AC")
                return Response(
                    {"status": 200, "message": "Friend requests accepted successfully"}
                )
            else:
                friendship = Relationship.objects.create(
                    sender=sender, receiver=receiver, status="PN"
                )
                friendship.save()
                return Response(
                    {"status": 200, "message": "Friend request sent successfully"}
                )
        except Gamer.DoesNotExist:
            return Response(
                {
                    "status": 404,
                    "message": "User not found",
                }
            )
        except Relationship.DoesNotExist:
            return Response(
                {
                    "status": 404,
                    "message": "Friend request not found",
                }
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": str(e),
                }
            )

    @method_decorator(jwt_cookie_required)
    def delete(self, request):
        try:
            sender_id = request.decoded_token["id"]
            receiver_id = request.data.get("target_id")
            sender = Gamer.objects.get(id=sender_id)
            receiver = Gamer.objects.get(id=receiver_id)
            try:
                friendship = Relationship.objects.get(sender=sender, receiver=receiver)
            except Relationship.DoesNotExist:
                friendship = Relationship.objects.get(sender=receiver, receiver=sender)
            if friendship:
                friendship.delete()
                return Response(
                    {"status": 204, "message": "Relationship deleted successfully"}
                )
            else:
                return Response(
                    {
                        "status": 404,
                        "message": "Friend request not found",
                    }
                )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": str(e),
                }
            )


class MatchesHistory(APIView):

    @method_decorator(jwt_cookie_required)
    def get(self, request):
        try:
            gamer = Gamer.objects.get(id=request.decoded_token["id"])
            matches = GamerMatch.objects.filter(
                gamer_id=gamer.id, match_id__state="PLY"
            ).order_by("-match_id__id")[:8]
            matches_data = []
            for match in matches:
                match_gamers = []
                for gamer_match in match.match_id.gamermatch_set.all():
                    match_gamers.append(
                        {
                            "id": gamer_match.gamer_id.id,
                            "username": gamer_match.gamer_id.username,
                            "avatar": gamer_match.gamer_id.avatar,
                            "score": gamer_match.score,
                            "won": gamer_match.won,
                        }
                    )
                matches_data.append(
                    {
                        "id": match.match_id.id,
                        "game": match.match_id.game,
                        "gamers": match_gamers,
                    }
                )
            return Response({"status": 200, "matches": matches_data})
        except Gamer.DoesNotExist:
            return Response(
                {
                    "status": 404,
                    "message": "User not found",
                }
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": str(e),
                }
            )
