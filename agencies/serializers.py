from rest_framework import serializers
from agencies.models import Agency , Inquiry
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


class InquiryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ('id' , 'message')
        read_only_fields = ('id',)


class InquiryListSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title' , read_only=True)
    property_slug = serializers.CharField(source='property.slug' , read_only=True)
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.CharField(source='customer.phone_number' , read_only=True)

    class Meta:
        model = Inquiry
        fields = ('id' , 'property_title' , 'property_slug' , 'customer_name' , 'customer_phone' ,
                  'message' , 'status' , 'created')

    def get_customer_name(self , obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"


class InquiryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ('status',)






