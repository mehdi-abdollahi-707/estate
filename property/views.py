from django.shortcuts import render, get_object_or_404
from django.db.models import F
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import Property , PropertyImage
from rest_framework.views import APIView
from rest_framework.response import Response
from agencies.models import Agency
from agencies.permissions import IsAgent
from .serializers import (CreatePropertySerializer, ListPropertySerializer,
                          PropertyDetailSerializer, PropertyUpdateSerializer)


def _get_request_agency(request):
    try:
        return request.user.agency
    except Agency.DoesNotExist:
        return None


class CreatePropertyView(APIView):
    permission_classes = [IsAgent]
    serializer_class = CreatePropertySerializer

    def post(self , request):
        agency = _get_request_agency(request)
        if agency is None:
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
        serializer = self.serializer_class(properties , many=True , context={'request':request})
        return Response(serializer.data , status=status.HTTP_200_OK)


class PropertyDetailView(APIView):
    """
    Public property detail view, identified by slug
    """
    permission_classes = [AllowAny]
    serializer_class = PropertyDetailSerializer

    def get(self , request , slug):
        property_obj = get_object_or_404(Property , slug=slug)

        Property.objects.filter(pk=property_obj.pk).update(view_count=F('view_count') + 1)
        property_obj.refresh_from_db(fields=['view_count'])

        serializer = self.serializer_class(property_obj , context={'request':request})
        return Response(serializer.data , status=status.HTTP_200_OK)


class UpdatePropertyView(APIView):
    """
    update property just for the owning agent
    """
    permission_classes = [IsAgent]
    serializer_class = PropertyUpdateSerializer

    def patch(self , request , slug):
        agency = _get_request_agency(request)
        if agency is None:
            return Response({"message":"Agency not found"}, status=status.HTTP_404_NOT_FOUND)

        property_obj = get_object_or_404(Property , slug=slug , agency=agency)

        serializer = self.serializer_class(instance=property_obj , data=request.data , partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data , status=status.HTTP_200_OK)


class DeletePropertyView(APIView):
    """
    delete property just for the owning agent
    """
    permission_classes = [IsAgent]

    def delete(self , request , slug):
        agency = _get_request_agency(request)
        if agency is None:
            return Response({"message":"Agency not found"}, status=status.HTTP_404_NOT_FOUND)

        property_obj = get_object_or_404(Property , slug=slug , agency=agency)
        property_obj.delete()
        return Response({"message":"Property deleted"}, status=status.HTTP_200_OK)
