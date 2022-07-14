from io import BytesIO
from uuid import uuid4

from api.permissions import CheckBinaryPermission, CheckImagePermission
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django_sendfile import sendfile
from PIL import Image
from rest_framework import decorators, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse



@decorators.api_view(["GET"])
@decorators.permission_classes([IsAuthenticated, CheckImagePermission])
def get_image(request, image_path: str):
    """
    Use X-SendFile to server media depending on the permissions
    """
    return sendfile(request, image_path, attachment=False, mimetype="image/jpeg")


@decorators.api_view(["GET"])
@decorators.permission_classes([IsAuthenticated, CheckImagePermission, CheckBinaryPermission])
def generate_binary_link(request, image_path: str):
    """
    Generate and return token that will be used to generate link to fetch binary image

    Time after image expries can be set using GET parameter "timeout", 
    e.g. ...?timeout=600 to set timeout=10minutes (600 seconds)
    """
    timeout = request.GET.get("timeout", 30)    # time to link expiration
    if not (300 <= timeout <= 3000):
        if timeout < 300:
            timeout = 300       # mininmal timeout is 300s
        else:
            timeout = 3000      # maximum timeout is 3000s

    token = str(uuid4())
    cache.set(token, image_path, timeout)
    return Response({
        "binary_image": reverse("get_binary_image", args=(token,)),
        "timeout": timeout,
        })


@decorators.api_view(["GET"])
@decorators.permission_classes([IsAuthenticated, CheckBinaryPermission])
def get_binary_image(request, token: str):
    """
    Check if token exists (could expire) and if True, return binary image 
    """
    image_path = cache.get(token)
    if image_path:
        return generate_binary_image(request, image_path)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)  # nothing to see here


@decorators.permission_classes([IsAuthenticated, CheckImagePermission, CheckBinaryPermission])
def generate_binary_image(request, image_path: str):
    """
    Load image from given path, convert to binary image 
    and send in HTTP response as binary data
    """
    img = Image.open(settings.MEDIA_ROOT / image_path)  # open image
    img_format = img.format
    
    img = img.convert('1')  # convert photo to binary: https://en.wikipedia.org/wiki/Binary_image
    buffer = BytesIO()
    img.save(buffer, format=img_format)     # save image to buffer
    mime_type = "image/png" if img_format == "PNG" else "image/jpeg"    # choose correct mimetype (only two available due to limited image formats)

    return HttpResponse(buffer.getvalue(), content_type=mime_type)      # send photo as binary data in http response, using Response() caused errors with encoding(?)
