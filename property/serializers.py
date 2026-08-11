from rest_framework import serializers
from .models import Property , PropertyImage
from django.db import transaction
from agencies.serializers import AgencyListSerializer
from .validators import validate_image_size



class CreatePropertySerializer(serializers.ModelSerializer):
    image1 = serializers.ImageField(write_only=True , validators=[validate_image_size])
    image2 = serializers.ImageField(write_only=True ,required=False , validators=[validate_image_size])
    image3 = serializers.ImageField(write_only=True ,required=False , validators=[validate_image_size])
    images = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Property
        fields = ('id' , 'slug' , 'title' , 'description' , 'listing_type' , 'property_type' ,
                  'status' , 'price' , 'area' , 'bedrooms' , 'bathrooms' ,
                  'has_parking' , 'floor' , 'total_floors' , 'year_built',
                  'province' , 'city' , 'address' , 'latitude' , 'longitude',
                  'image1' , 'image2' , 'image3' , 'images' ,)
        read_only_fields = ('id' , 'slug')

    def get_images(self , obj):
        images = obj.images.all()
        return ImageSerializer(images , many=True , context=self.context).data

    @transaction.atomic
    def create(self, validated_data):
        agency = self.context.get('agency')
        validated_data['agency'] = agency

        image1 = validated_data.pop('image1')
        image2 = validated_data.pop('image2', None)
        image3 = validated_data.pop('image3', None)

        prop = Property.objects.create(**validated_data)

        PropertyImage.objects.create(property=prop, image=image1, is_first=True)

        for image in (image2, image3):
            if image:
                PropertyImage.objects.create(property=prop, image=image)

        return prop

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ('image' , )


class ListPropertySerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = ('id' , 'slug' , 'title' , "description" , 'listing_type' , 'property_type' , 'status' , 'price' , 'images')

    def get_images(self , obj):
        images = obj.images.all()
        return ImageSerializer(images , many=True , context=self.context).data


class PropertyDetailSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    agency = AgencyListSerializer(read_only=True)

    class Meta:
        model = Property
        fields = ('id' , 'slug' , 'title' , 'description' , 'listing_type' , 'property_type' ,
                  'status' , 'price' , 'area' , 'bedrooms' , 'bathrooms' , 'has_parking' ,
                  'floor' , 'total_floors' , 'year_built' , 'province' , 'city' , 'address' ,
                  'latitude' , 'longitude' , 'is_featured' , 'view_count' , 'created' , 'updated' ,
                  'agency' , 'images')

    def get_images(self , obj):
        images = obj.images.all()
        return ImageSerializer(images , many=True , context=self.context).data


class PropertyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ('title' , 'description' , 'listing_type' , 'property_type' , 'status' ,
                  'price' , 'area' , 'bedrooms' , 'bathrooms' , 'has_parking' , 'floor' ,
                  'total_floors' , 'year_built' , 'province' , 'city' , 'address' ,
                  'latitude' , 'longitude')