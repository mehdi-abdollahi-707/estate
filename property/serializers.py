from rest_framework import serializers
from .models import Property , PropertyImage
from django.db import transaction



class CreatePropertySerializer(serializers.ModelSerializer):
    image1 = serializers.ImageField(write_only=True)
    image2 = serializers.ImageField(write_only=True ,required=False)
    image3 = serializers.ImageField(write_only=True ,required=False)

    class Meta:
        model = Property
        fields = ('title' , 'description' , 'listing_type' , 'property_type' ,
                  'status' , 'price' , 'area' , 'bedrooms' , 'bathrooms' ,
                  'has_parking' , 'floor' , 'total_floors' , 'year_built',
                  'province' , 'city' , 'address' , 'latitude' , 'longitude',
                  'is_featured' , 'image1' , 'image2' , 'image3' ,)

    @transaction.atomic
    def create(self, validated_data):
        agency = self.context.get('agency')
        validated_data['agency'] = agency

        image1 = validated_data.pop('image1')
        image2 = validated_data.pop('image2', None)
        image3 = validated_data.pop('image3', None)

        prop = Property.objects.create(**validated_data)


        PropertyImage.objects.create(property=prop, image=image1)

        for image in (image2, image3):
            if image:
                PropertyImage.objects.create(property=prop, image=image)

        return prop


