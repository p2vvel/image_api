from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
import uuid
import os
from .utils import delete_file
from django.core.exceptions import ValidationError
from .utils import get_resized_image


class AvailableHeight(models.Model):
    def deny_base_height(value) -> None:
        """
        Don't let user to create a 200px entry
        It'll always be available as a part of basic tier
        """
        if value == 200:
            raise ValidationError("Height already available!")

    height = models.IntegerField(validators=[MinValueValidator(10), deny_base_height], unique=True)      # available height of the image, minimum height is 10px
    
    def __str__(self) -> str:
        return f"Height: {self.height}px"


class Tier(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)        # tier name
    binary_image = models.BooleanField(default=False, null=False)           # is binary image available?
    original_image = models.BooleanField(default=False, null=False)         # is original image available?
    available_heights = models.ManyToManyField(to=AvailableHeight, blank=True)          # available image heights (different idea => ArrayField => worse portability(only Postgres))

    def __str__(self) -> str:
        return f"'{self.name}' tier"

    @property
    def extra_image_sizes(self) -> list[int]:
        """
        Returns list of available image height (in active tier), 
        200px is not included as it is always available in Basic Tier
        """
        query = self.available_heights.all().values_list("height", flat=True)
        return list(query)


class User(AbstractUser):
    tier = models.ForeignKey(to=Tier, default=None, null=True, blank=True, on_delete=models.SET_NULL)   # null = basic tier
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, null=False)


    def save(self, *args, **kwargs) -> None:
        """
        Overriden to generate thumbnails when tier changes
        """
        # if saving existing object
        if not self._state.adding:
            # compare current resolutions with old ones (still stored in db)
            old_data = User.objects.get(pk=self.pk)
            previous_resolutions = [] if old_data.tier is None else old_data.tier.extra_image_sizes

            # check if there's any tier at all (no tier = Basic tier)
            if self.tier:
                new_res = set(self.tier.extra_image_sizes)              # currently available resolutions
                old_res = set(previous_resolutions)        # previously available resolutions
                if new_res != old_res:
                    unavailable_res = new_res.difference(old_res)
                    for res in unavailable_res:
                        images = self.uploadedimage_set.filter(parent=None)     # all original images
                        # TODO: check if image size doesnt exist!
                        for img in images:
                            # check if image has thumbnail with requested size (maybe user returned to previous tier and file already exists)
                            if res not in img.uploadedimage_set.all().values_list("height", flat=True):
                                UploadedImage.objects.create(
                                    image = get_resized_image(img.image, res),
                                    owner = img.owner,
                                    title = img.title,
                                    parent = img,
                                )

        return super().save(*args, **kwargs)



class UploadedImage(models.Model):
    def upload_to(instance, filename):
        new_filename = uuid.uuid4()
        ext = os.path.splitext(filename)[1]
        return f"{instance.owner.uuid}/{new_filename}{ext}"

    def get_title(instance, filename):
        return filename

    def delete(self, *args, **kwargs):
        delete_file(self.image.path)    # delete original image from storage
        if not self.parent:
            thumbnails = self.uploadedimage_set.all()
            for t in thumbnails:
                    delete_file(t.image.path)   # delete thumbnails' files:
        return super().delete(*args, **kwargs)


    image = models.ImageField(upload_to=upload_to, height_field="height")
    title = models.TextField(null=False, blank=False)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)        # user that uploaded image
    parent = models.ForeignKey("self", default=None, null=True, blank=True, on_delete=models.CASCADE)   # null = original picture
    height = models.IntegerField(default=0)     # automatically filled
