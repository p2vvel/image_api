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


# def clean(self):
#         """Added image format checking. Only PNG, JPEG and GIF formats allowed"""
#         super().clean()
#         if self.original_image: # image has to be uploaded
#             try:
#                 img = Image.open(self.original_image)
#                 if img.format not in ["JPEG", "PNG", "GIF"]:
#                     raise ValidationError({"original_image": "Wrong image format!"})
#             except UnidentifiedImageError:
#                 raise ValidationError("Wrong image file!")  # raised if 'image' appears to be .pdf, .exe or other non-image file
#             except ValidationError:
#                 raise   # pass exception up
#             except Exception as e:
#                 raise ValidationError("Error while validating!")    # other errors
#         else:
#             raise ValidationError({"original_image": "No image uploaded!"})


