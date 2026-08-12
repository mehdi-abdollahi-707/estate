from rest_framework import serializers
from .models import SaveProperty


class SavePropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = SaveProperty
        fields = ["id", "property", "created"]
        # all fields are set by the view/DB (property from the URL slug, user from
        # the request, created is auto_now_add) - never accepted as client input
        read_only_fields = fields
