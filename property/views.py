from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import Property , PropertyImage
from rest_framework.views import APIView
from rest_framework.response import Response
from agencies.models import Agency
from agencies.permissions import IsAgent
from .serializers import CreatePropertySerializer, ListPropertySerializer


class CreatePropertyView(APIView):
    permission_classes = [IsAgent]
    serializer_class = CreatePropertySerializer

    def post(self , request):
        try:
            agency = request.user.agency
        except Agency.DoesNotExist:
            return Response({"message":"Agency not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data , context={'agency':agency})
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data , status=status.HTTP_201_CREATED)


class ListPropertyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ListPropertySerializer

    def get(self , request):
        properties = Property.objects.exclude(status=Property.Status.INACTIVE)
        serializer = self.serializer_class(properties , many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)
