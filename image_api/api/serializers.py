from rest_framework import serializers
from .models import UploadedImage
from PIL import Image, UnidentifiedImageError



class ImageSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ["image"]

    def validate_image(self, value):
        try:
            img = Image.open(value)
        except UnidentifiedImageError:
            # PIL will raise that exception if file is not an image
            raise serializers.ValidationError("Wrong image file! Probably not an image!")
        except:
            # couldn't load an image
            raise serializers.ValidationError("Problem with loading image!")

        # only PNG and JPEG allowed
        if img.format not in ["JPEG", "PNG"]:
            raise serializers.ValidationError(f"Unsupported image format! Must be JPEG or PNG, currently {img.format}.")

        return value


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ["title", "image"]