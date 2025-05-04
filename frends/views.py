from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Frends
from members.models import CustomUser
from rest_framework.permissions import IsAuthenticated



from admin.neo4j_utils import Neo4jClient  # Make sure to import your Neo4j client

class AddFollowingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_user_ida = request.data.get('target_user_id')
        target_user = get_object_or_404(CustomUser, id=target_user_ida)
        print(target_user)
        # Validate target_user_id
        if not target_user_ida or not isinstance(target_user_ida, int):
            return Response({"error": "Invalid 'target_user_id' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        user_friends, created = Frends.objects.get_or_create(userid=request.user)
        if created:
            user_friends.settings = {
                "accept_followers": True,
                "block": []
            }
            user_friends.save()
        if isinstance(user_friends.settings, dict) and user_friends.settings.get('accept_followers', True):
            if {"uid":target_user.id,"name":target_user.username} not in user_friends.following:
                user_friends.following.append( {"uid":target_user.id,"name":target_user.username})
                user_friends.save()
                message = "success"

                # Create the relationship in Neo4j
                neo4j_client = Neo4jClient()
                neo4j_client.create_relationship(request.user.id, target_user.id, "FOLLOWS")
                neo4j_client.close()
            else:
                message = "You are already following this user"
            print(message)
        return Response({"message": message,"data":user_friends.following}, status=status.HTTP_200_OK)

from django.shortcuts import get_object_or_404

class AddFollowerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_user_id = request.data.get('target_user_id')

        # Validate target_user_id
        if not target_user_id or not isinstance(target_user_id, int):
            return Response({"error": "Invalid 'target_user_id' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the CustomUser instance
        target_user = get_object_or_404(CustomUser, id=target_user_id)

        # Get or create the Frends instance for the target user
        target_friends, created = Frends.objects.get_or_create(userid=target_user)

        if created:
            target_friends.settings = {
                "accept_followers": True,
                "block": []
            }
            target_friends.save()

        if request.user.id not in target_friends.followers:
            target_friends.followers.append({"idd":request.user.id,"name":request.user.username})
            target_friends.save()
            message = "Follower added successfully"

            # Optionally create the relationship in Neo4j as well
            neo4j_client = Neo4jClient()
            neo4j_client.create_relationship(target_user_id, request.user.id, "FOLLOWER_OF")
            neo4j_client.close()
        else:
            message = "You are already a follower of this user"

        return Response({"message": message}, status=status.HTTP_200_OK)


class Settings(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        accept_follwers = request.data.get('accept_follwers')
        user_friends, _ = Frends.objects.get_or_create(userid=request.user)
        if accept_follwers == 'true':
            user_friends.accept_follwers = True
        else:
            user_friends.accept_follwers = False
        user_friends.save()
        return Response({"message": "Settings updated successfully"}, status=status.HTTP_200_OK)


class Settingsblock(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        block = request.data.get('block')
        user_friends, _ = Frends.objects.get_or_create(userid=request.user)
        user_friends['block']=[block]
        user_friends.save()
        return Response({"message": "Settings updated successfully"}, status=status.HTTP_200_OK)


class UnFollowingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_user_id = request.data.get('target_user_id')

        if not target_user_id:
            return Response(
                {"error": "Target user ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the current user's Frends object
        user = request.user
        frends_obj = get_object_or_404(Frends, userid=user)

        # Find and remove the target user from the following list
        following_list = frends_obj.following
        updated_following = [
            user for user in following_list if user.get('uid') != target_user_id
        ]

        if len(following_list) == len(updated_following):
            return Response(
                {"message": "User not found in the following list."},
                status=status.HTTP_200_OK,
            )

        # Update and save the following list
        frends_obj.following = updated_following
        frends_obj.save()
        neo4j_client = Neo4jClient()
        neo4j_client.delete_relationship( request.user.id,target_user_id,)
        # neo4j_client.print_connected_nodes(request.user.id)
        # neo4j_client.delete_relationship( target_user_id,request.user.id)

        neo4j_client.close()
        return Response(
            {"message": "success","data":updated_following},
            status=status.HTTP_200_OK,
        ) 

