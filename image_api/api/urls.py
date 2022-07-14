from django.urls import path
from rest_framework import routers
from .views import ImageViewset, get_binary_image, get_image, generate_binary_link



router = routers.SimpleRouter()
router.register(r'', ImageViewset, basename="images")

urlpatterns = [
    path("images/<path:image_path>", get_image, name="get_image"),
    path("generate/<path:image_path>", generate_binary_link, name="generate_binary_link"),
    path("binary/<str:token>", get_binary_image, name="get_binary_image"),
]

urlpatterns += router.urls