from django.shortcuts import render, get_object_or_404
from django.db.models import F
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
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


def _int_query_param(request, name):
    value = request.query_params.get(name)
    if value in (None, ''):
        return None
    try:
        return int(value)
    except ValueError:
        raise ValidationError({name: "Must be an integer."})


class PropertyPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CreatePropertyView(APIView):
    permission_classes = [IsAgent]
    serializer_class = CreatePropertySerializer

    def post(self , request):
        agency = _get_request_agency(request)
        if agency is None:
            return Response({"message":"Agency not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data , context={'agency':agency , 'request':request})
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data , status=status.HTTP_201_CREATED)


class ListPropertyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = ListPropertySerializer
    pagination_class = PropertyPagination

    def get(self , request):
        properties = Property.objects.exclude(status=Property.Status.INACTIVE)

        listing_type = request.query_params.get('listing_type')
        if listing_type:
            properties = properties.filter(listing_type=listing_type)

        property_type = request.query_params.get('property_type')
        if property_type:
            properties = properties.filter(property_type=property_type)

        province = request.query_params.get('province')
        if province:
            properties = properties.filter(province=province)

        city = request.query_params.get('city')
        if city:
            properties = properties.filter(city=city)

        min_price = _int_query_param(request, 'min_price')
        if min_price is not None:
            properties = properties.filter(price__gte=min_price)

        max_price = _int_query_param(request, 'max_price')
        if max_price is not None:
            properties = properties.filter(price__lte=max_price)

        bedrooms = _int_query_param(request, 'bedrooms')
        if bedrooms is not None:
            properties = properties.filter(bedrooms=bedrooms)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(properties, request, view=self)
        serializer = self.serializer_class(page , many=True , context={'request':request})
        return paginator.get_paginated_response(serializer.data)


class PropertyDetailView(APIView):
    """
    Public property detail view, identified by slug
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = PropertyDetailSerializer

    def get(self , request , slug):
        property_obj = get_object_or_404(
            Property.objects.exclude(status=Property.Status.INACTIVE) , slug=slug
        )

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
