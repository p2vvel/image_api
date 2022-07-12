from io import BytesIO

from django.core.files.base import File
from django.http import HttpResponse
from PIL import Image
from rest_framework import mixins, permissions, viewsets

from .models import UploadedImage
from .serializers import ImageSerializer, ImageSerializerCreate
from .utils import get_resized_image
from django_sendfile import sendfile

from rest_framework import status
from rest_framework.response import Response
from rest_framework import decorators
from rest_framework.permissions import IsAuthenticated



class ImageViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]      # allow only logged users to use the API
    queryset = UploadedImage.objects.all()                  # base queryset 
    serializer_class = ImageSerializerCreate

    def get_queryset(self):
        """
        Filter images to show only owned by the current user
        """
        queryset = super().get_queryset()
        return queryset.filter(owner = self.request.user)
    
    def perform_create(self, serializer):
        """
        Override default function to add owner and title info. Recommended by DRF tutorial: 
        https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/#associating-snippets-with-users
        """
        original_image = serializer.save(
                            owner=self.request.user, 
                            title=self.request.FILES.get("image").name
                            ) # adding owner and title info to images

        user_tier = original_image.owner.tier
        
        # Basic tier - always create 200px thumbnail
        UploadedImage.objects.create(
            image=get_resized_image(original_image.image, 200),
            owner = original_image.owner,
            title = original_image.title,
            parent=original_image
        )

        if user_tier is not None:
            # custom tier - create all thumbnails
            thumbnail_sizes = list(user_tier.available_heights.all().values_list("height", flat=True))
            for size in thumbnail_sizes:
                UploadedImage.objects.create(
                image=get_resized_image(original_image.image, size),
                owner = original_image.owner,
                title = original_image.title,
                parent=original_image
            )

        return original_image

    def get_serializer_class(self, *args, **kwargs):
        """
        Return different serializer (thus different data) depending on action
        """
        if self.action == "create":
            return ImageSerializerCreate
        else:
            return ImageSerializer



@decorators.api_view(["GET"])
@decorators.permission_classes([IsAuthenticated])
def get_binary_image(request, user_uuid: str, image_name: str):
    image_object = UploadedImage.objects.get(image=f"{user_uuid}/{image_name}")
    
    img = Image.open(image_object.image)
    img_format = img.format
    
    img = img.convert('1')  # convert photo to binary: https://en.wikipedia.org/wiki/Binary_image
    buffer = BytesIO()
    img.save(buffer, format=img_format)     # save image to buffer
    mime_type = "image/png" if img_format == "PNG" else "image/jpeg"    # choose correct mimetype (only two available due to limited image formats)

    return Response(buffer.getvalue(), content_type=mime_type)      # send photo as binary data in http response



@decorators.api_view(["GET"])
@decorators.permission_classes([IsAuthenticated])
def get_image(request, image_path: str):
    img = UploadedImage.objects.get(image=image_path)
    if img.owner == request.user:
        return sendfile(request, image_path, attachment=False, mimetype="image/jpeg")
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)  # nothing to see here