from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import UploadedImage



class CheckImagePermission(permissions.BasePermission):
    """
    Check if user is owner of the image and
    check if user has rights to see requested image size

    Not for later use, based on views' arguments!
    """
    def has_permission(self, request, view):
        image_path = view.kwargs.get("image_path")  # 
        if not image_path:
            return False        # if there's no argument 'image_path', deny access

        image_object = get_object_or_404(UploadedImage, image=image_path)

        # check if user is an owner of the photo
        if image_object.owner == request.user:
            # 200px thumbnails are always available:
            if image_object.height == 200: return True     
            
            user_tier = request.user.tier
            if user_tier:
                # request for original photo
                if image_object.parent is None:
                    return user_tier.original_image     # grant access if proper tier
                else:
                    # different sizes has to be checked
                    return image_object.height in user_tier.extra_image_sizes   # access depends on tier

        return False    # deny access if it hasn't been already given
            

class CheckBinaryPermission(permissions.BasePermission):
    """
    Check if user has permission to generate and view binary images
    """
    def has_permission(self, request, view):
        if request.user.tier:
            return request.user.tier.binary_image
        else:
            return False
