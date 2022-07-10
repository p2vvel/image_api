from django.db import models
from django.contrib.auth.models import AbstractUser



class AvailableHeight(models.Model):
    height = models.IntegerField()      # available height of the image
    
    def __str__(self) -> str:
        return f"Height: {self.height}px"


class Tier(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)        # tier name
    binary_image = models.BooleanField(default=False, null=False)           # is binary image available?
    original_image = models.BooleanField(default=False, null=False)         # is original image available?
    available_heights = models.ManyToManyField(to=AvailableHeight)          # available image heights (different idea => ArrayField => worse portability(only Postgres))

    def __str__(self) -> str:
        return f"'{self.name}' tier"


class User(AbstractUser):
    tier = models.ForeignKey(to=Tier, default=None, null=True, blank=True, on_delete=models.SET_NULL)   # null = basic tier


class UploadedImage(models.Model):
    image = models.ImageField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)        # user that uploaded image

