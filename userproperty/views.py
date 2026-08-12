from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from property.models import Property
from django.shortcuts import get_object_or_404
from .models import SaveProperty
from .serializers import SavePropertySerializer


class UserSaveProperty(APIView):
    permission_classes = [IsAuthenticated]

    def post(self , request , slug):
        property = get_object_or_404(Property , slug = slug)

        # ownership lives on Property.agency.agent, not Property itself - Property has no direct user FK
        if property.agency.agent == request.user:
            return Response({"message" : "You can't save this property"} , status = status.HTTP_403_FORBIDDEN)

        # get_or_create + the (user, property) unique constraint together make this safe
        # to call repeatedly without creating duplicate saves or racing another request
        obj , created = SaveProperty.objects.get_or_create(user=request.user ,
                                                           property = property)
        data = SavePropertySerializer(obj).data

        if created:
            return Response({"message" : "Property was successfully added" , **data} , status = status.HTTP_201_CREATED)

        return Response({"message" : "Property was already added" , **data} , status = status.HTTP_200_OK)
