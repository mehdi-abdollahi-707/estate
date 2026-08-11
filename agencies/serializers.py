from rest_framework import serializers
from agencies.models import Agency
from rest_framework.serializers import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ('name' , 'license_number' , 'business_phone' , 'description' , 'province' , 'city' , 'exact_address')


class AgencyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ('pk' , 'name' , "province" , 'city')



class AgencyDetailSerializer(serializers.ModelSerializer):
    """Full agency detail, for the owning agent."""
    class Meta:
        model = Agency
        fields = "__all__"


class AgencyPublicDetailSerializer(serializers.ModelSerializer):
    """Public agency detail — excludes internal fields such as the owning agent's user id."""
    class Meta:
        model = Agency
        fields = ('pk' , 'name' , 'license_number' , 'business_phone' , 'description' ,
                  'province' , 'city' , 'exact_address' , 'is_verified' , 'created' , 'updated')






