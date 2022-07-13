from io import BytesIO
from uuid import uuid4

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django_sendfile import sendfile
from PIL import Image
from rest_framework import decorators, mixins, permissions, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import UploadedImage
from .permissions import CheckBinaryPermission, CheckImagePermission
from .serializers import ImageSerializer, ImageSerializerCreate
from .utils import get_resized_image


class ImageViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]      # allow only logged users to use the API
    queryset = UploadedImage.objects.all()                  # base queryset 
    serializer_class = ImageSerializerCreate

    def get_queryset(self):
        """
        Filter images to show only owned by the current user
        """
        queryset = super().get_queryset()
        return queryset.filter(owner = self.request.user, parent=None)
    
    def perform_create(self, serializer):
        """
        Override default function to add owner and title info. Recommended by DRF tutorial: 
        https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/#associating-snippets-with-users
        """
        original_image = serializer.save(
                            owner=self.request.user, 
                            title=self.request.FILES.get("image").name
                            ) # adding owner and title info to images
        
        # Basic tier - always create 200px thumbnail
        UploadedImage.objects.create(
            image=get_resized_image(original_image.image, 200),
            owner = original_image.owner,
            title = original_image.title,
            parent=original_image
        )

        if original_image.owner.tier is not None:
            # custom tier - create all thumbnails
            thumbnail_sizes = original_image.owner.tier.extra_image_sizes
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
@decorators.permission_classes([IsAuthenticated, CheckImagePermission])
def get_image(request, image_path: str):
    """
    Serve media files (photos) using X-SendFile, allows to limit access to 
    resources and still benefit from external server performance (e.g. nginx)
    """
    return sendfile(request, image_path, attachment=False, mimetype="image/jpeg")



@decorators.api_view(["GET"])
@decorators.permission_classes([IsAuthenticated, CheckImagePermission, CheckBinaryPermission])
def generate_binary_link(request, image_path: str):
    """
    Generate link to binary version of the image
    """
    timeout = request.GET.get("timeout", 30)    # time to link expiration

    token = str(uuid4())
    cache.set(token, image_path, timeout)
    return Response({
        "binary_image": reverse("get_binary_image", args=(token,)),
        "timeout": timeout,
        })


@decorators.api_view(["GET"])
@decorators.permission_classes([IsAuthenticated, CheckBinaryPermission])
def get_binary_image(request, token: str):
    image_path = cache.get(token)
    if image_path:
        return generate_binary_image(request, image_path)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)  # nothing to see here


@decorators.permission_classes([IsAuthenticated, CheckImagePermission, CheckBinaryPermission])
def generate_binary_image(request, image_path: str):
    img = Image.open(settings.MEDIA_ROOT / image_path)  # open image
    img_format = img.format
    
    img = img.convert('1')  # convert photo to binary: https://en.wikipedia.org/wiki/Binary_image
    buffer = BytesIO()
    img.save(buffer, format=img_format)     # save image to buffer
    mime_type = "image/png" if img_format == "PNG" else "image/jpeg"    # choose correct mimetype (only two available due to limited image formats)

    return HttpResponse(buffer.getvalue(), content_type=mime_type)      # send photo as binary data in http response, using Response() caused errors with encoding(?)
