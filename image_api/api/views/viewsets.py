from api.models import UploadedImage
from api.serializers import ImageSerializer, ImageSerializerCreate
from api.utils import get_resized_image
from rest_framework import mixins, permissions, viewsets
from rest_framework.response import Response

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

    def create(self, request, *args, **kwargs):
        """
        Overriden to provide the same data representation on create, 
        as it is normally on list and retrieve

        Source: https://stackoverflow.com/a/56439689
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        instance_serializer = ImageSerializer(instance)
        return Response(instance_serializer.data)