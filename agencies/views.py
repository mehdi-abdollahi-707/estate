from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import AgencySerializer , AgencyDetailSerializer , AgencyListSerializer , AgencyPublicDetailSerializer
from .permissions import IsAgent
from django.shortcuts import get_object_or_404

class CreateAgencyView(APIView):
    """
    create agency just for authenticated agent
    """
    permission_classes = [IsAgent]
    serializer_class = AgencySerializer

    def post(self , request):
        if Agency.objects.filter(agent = request.user).exists():
            return Response({"message" : "you already have an agency"} , status = status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data , context={'request':request})
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save(agent = request.user)
        except IntegrityError:
            return Response({"message" : "you already have an agency"} , status = status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data , status=status.HTTP_201_CREATED)


class UpdateAgencyView(APIView):
    """
    update agency just for authenticated agent
    """
    permission_classes = [IsAgent]
    serializer_class = AgencySerializer

    def patch(self , request):
        try:
            agency = request.user.agency
        except Agency.DoesNotExist:
            return Response({"message":"Agency not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=agency ,
                                           data = request.data ,
                                           partial=True,
                                           context={'request':request} ,)
        serializer.is_valid(raise_exception=True)

        changed = any(
            getattr(agency, field) != value
            for field, value in serializer.validated_data.items()
        )

        save_kwargs = {'is_verified': False} if changed and agency.is_verified else {}
        serializer.save(**save_kwargs)
        return Response(serializer.data , status=status.HTTP_200_OK)


class ListAgencyView(APIView):
    serializer_class = AgencyListSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self , request):
        agencies = Agency.objects.filter(is_verified = True)
        serializer = self.serializer_class(agencies , many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)


class DetailPublicAgencyView(APIView):
    """
    Public agency detail view
    """
    serializer_class = AgencyPublicDetailSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self , request , *args , **kwargs ):
        agency = get_object_or_404(Agency ,pk = kwargs['pk'] , is_verified = True)
        serializer = self.serializer_class(agency)
        return Response(serializer.data , status=status.HTTP_200_OK)


class DetailPrivetAgencyView(APIView):
    serializer_class = AgencyDetailSerializer
    permission_classes = [IsAgent]

    def get(self, request):
        try:
            agency = request.user.agency
        except Agency.DoesNotExist:
            return Response({"message":"Agency not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(agency)
        return Response(serializer.data , status=status.HTTP_200_OK)


class DeleteAgencyView(APIView):
    permission_classes = [IsAgent]

    def delete(self , request):
        try:
            agency = request.user.agency
            agency.delete()
        except Agency.DoesNotExist:
            return Response({"message":"Agency not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message":"Agency deleted"}, status=status.HTTP_200_OK)