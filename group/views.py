from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Groups,Acceptances
from .serializers import GroupSerializer,AcceptanceSerializer
from django.shortcuts import get_object_or_404

# Create Group View
class GroupCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(userid=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Update Group (name and members only) View
class GroupUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        group = get_object_or_404(Groups, pk=pk)

        # Allow only 'name' and 'members' to be updated
        data = request.data
        if 'name' in data:
            group.name = data['name']
        if 'members' in data:
            group.members = data['members']

        group.save()
        return Response({"message": "Group updated successfully"}, status=status.HTTP_200_OK)

# Delete Group View
class GroupDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        group = get_object_or_404(Groups, pk=pk)
        group.delete()
        return Response({"message": "Group deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Groups, Acceptances
from members.models import CustomUser  # Import your CustomUser model

class Accept(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        gid = data.get('gid')
        sts = data.get('status')
        print(data)

        # Validate gid and status
        if gid is None or not isinstance(gid, int):
            return Response({"error": "Invalid or missing 'gid' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        if sts is None or not isinstance(sts, int) or sts not in [0, 1]:
            return Response({"error": "Invalid or missing 'status' parameter; must be 0 or 1"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the group by gid
        group = Groups.objects.filter(id=gid).first()
        if not group:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the user is in the members list and update their status
        user_uid = request.user.id
        member_found = False
        print(user_uid)
        print(group)

        # Update the status in the members list
        for member in group.members:
            print(member['uid'])
            print(member["uid"] == user_uid)
            if member["uid"] == user_uid:
                print("hi")
                member["status"] = sts  # Update the status
                member_found = True
                break

        # If user is not found in the members list
        if not member_found:
            return Response({"error": "User not in group members"}, status=status.HTTP_400_BAD_REQUEST)

        # Save the updated group members list
        group.members = group.members  # Ensure the updated members list is assigned
        try:
            group.save()
        except Exception as e:
            return Response({"error": f"Failed to save group data: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Handle Acceptance record based on status
        try:
            # Get the user instance
            user_instance = CustomUser.objects.get(id=user_uid)

            if sts == 1:
                Acceptances.objects.get_or_create(userid=user_instance, gid=group)  # Use the user instance
            else:
                Acceptances.objects.filter(userid=user_instance, gid=group).delete()  # Use the user instance
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed to update acceptance record: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "User status updated successfully"}, status=status.HTTP_200_OK)

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Groups, Acceptances
from .serializers import GroupSerializer, AcceptanceSerializer
from frends.models import Frends
from frends.serializers import FrendSerializer
class getgroup_accept_frends_details(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        group = Groups.objects.filter(userid=user)

        # Serialize the Group objects
        group_serializer = GroupSerializer(group, many=True)

        acceptances = Acceptances.objects.filter(userid=user)

        # Serialize the Acceptance objects
        acceptance_serializer = AcceptanceSerializer(acceptances, many=True)


        fre=Frends.objects.filter(userid=user)
        ser=FrendSerializer(fre,many=True)
        # Combine serialized data into a single dictionary
        data = {
            "groups": group_serializer.data,
            "acceptances": acceptance_serializer.data,
            "frend":ser.data
        }
        print(data)
        # Return combined data
        return Response(data, status=status.HTTP_200_OK)
