from django.db.models.signals import m2m_changed
from .models import AvailableHeight, Tier, UploadedImage
from .utils import get_resized_image


def signal(sender, instance, **kwargs):  
    if kwargs["action"] == "pre_add":
        pk = kwargs["pk_set"]
        new_res = AvailableHeight.objects.filter(pk__in=pk).values_list("height", flat=True)
        for res in new_res:
            images = UploadedImage.objects.filter(parent=None, owner__tier=instance)     # all original images
            for img in images:
                # check if image has thumbnail with requested size (maybe user returned to previous tier and file already exists)
                if res not in img.uploadedimage_set.all().values_list("height", flat=True):
                    UploadedImage.objects.create(
                        image = get_resized_image(img.image, res),
                        owner = img.owner,
                        title = img.title,
                        parent = img,
                    )



m2m_changed.connect(signal, sender=Tier.available_heights.through)