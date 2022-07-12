from curses.ascii import HT
from django.http import HttpResponse
from django.shortcuts import render

from .serializers import ImageSerializerCreate, ImageSerializer
from .models import UploadedImage

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import permissions

from PIL import Image
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
        Return different data depending on action
        """
        if self.action == "create":
            return ImageSerializerCreate
        else:
            return ImageSerializer
