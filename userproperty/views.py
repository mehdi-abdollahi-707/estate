from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from property.models import Property
from django.shortcuts import get_object_or_404
from .models import SaveProperty
from .serializers import SavePropertySerializer, SavePropertyListSerializer


class SavePropertyPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserSaveProperty(APIView):
    permission_classes = [IsAuthenticated]

    def post(self , request , slug):
        property = get_object_or_404(Property , slug = slug)

        if property.agency.agent == request.user:
            return Response({"message" : "You can't save this property"} , status = status.HTTP_403_FORBIDDEN)

        obj , created = SaveProperty.objects.get_or_create(user=request.user ,
                                                           property = property)
        data = SavePropertySerializer(obj).data

        if created:
            return Response({"message" : "Property was successfully added" , **data} , status = status.HTTP_201_CREATED)

        return Response({"message" : "Property was already added" , **data} , status = status.HTTP_200_OK)



class ListSavedPropertiesView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SavePropertyListSerializer
    pagination_class = SavePropertyPagination

    def get(self , request):
        saved_properties = SaveProperty.objects.filter(user = request.user).select_related('property').prefetch_related('property__images').order_by('-created')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(saved_properties , request , view = self)
        serializer = self.serializer_class(page , many = True , context = {'request' : request})
        return paginator.get_paginated_response(serializer.data)


class UserUnsaveProperty(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self , request , pk):
        save_property = get_object_or_404(SaveProperty , pk = pk , user = request.user)
        save_property.delete()
        return Response({"message" : "Property was successfully unsaved"} , status = status.HTTP_200_OK)