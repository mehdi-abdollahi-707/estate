from rest_framework import serializers
from .models import SaveProperty
from property.serializers import ListPropertySerializer


class SavePropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = SaveProperty
        fields = ["id", "property", "created"]
        read_only_fields = fields


class SavePropertyListSerializer(serializers.ModelSerializer):
    property = ListPropertySerializer(read_only=True)

    class Meta:
        model = SaveProperty
        fields = ["id", "property", "created"]
        read_only_fields = fields
