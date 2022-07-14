from rest_framework import serializers
from .models import UploadedImage
from PIL import Image, UnidentifiedImageError
from django.conf import settings
from django.db.models import ImageField
from rest_framework.reverse import reverse




class ImageSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ["image"]

    def validate_image(self, value):
        """
        Image must be in PNG or JPEG format
        """
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
        fields = ["title"]

    def get_full_image_address(self, image: ImageField) -> str:
        """
        Create full URL address to image
        """
        # return reverse("get_image", args=(image.name,))
        return reverse("get_image", args=(image.name,))

    def get_resolution_representation(self, image: ImageField, binary: bool) -> dict:
        """
        For given image return dict in format {
            "url": <url_to_image>, 
            "binary": <url_to_generate_binary_image>,   <== *optional 
            }
        """
        temp = {}

        temp["url"] = self.get_full_image_address(image.image)
        if binary:
            temp["binary"] = reverse("generate_binary_link", args=(image.image.name,))
        return temp


    def to_representation(self, instance):
        """
        Add links to all available for user resolutions
        """
        data = super().to_representation(instance)  # default returned json
        resolutions = {}

        binary_image = False if instance.owner.tier is None else instance.owner.tier.binary_image
        
        # always available 200px thumbnail
        thumbnail = instance.uploadedimage_set.get(height=200)
        resolutions["200px"] = self.get_resolution_representation(thumbnail, binary_image)
        
        # check user tier for more resolutions
        user_tier = instance.owner.tier
        if user_tier:
            # user has rights to get original image
            if user_tier.original_image:
                resolutions["original"] = self.get_resolution_representation(instance, binary_image)
            # return links to other thumbnail sizes
            for t in instance.owner.tier.extra_image_sizes:
                thumbnail = instance.uploadedimage_set.get(height=t)
                resolutions[f"{t}px"] = self.get_resolution_representation(thumbnail, binary_image)

        data["resolutions"] = resolutions
        return data