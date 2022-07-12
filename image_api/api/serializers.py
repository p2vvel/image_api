from rest_framework import serializers
from .models import UploadedImage



class ImageSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ["image"]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ["title", "image"]


    def validate_image(self, value):
        if False:
            raise serializers.ValidationError("False error")
        return value

