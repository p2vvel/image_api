from django.db.models.signals import m2m_changed
from .models import AvailableHeight, Tier, UploadedImage
from .utils import get_resized_image



def signal(sender, instance, **kwargs):
    """
    Handle tier extend - if new resolution is added to a tier, all images 
    in the tier have to be processed because new thumbnails have to be created
    """
    if kwargs["action"] == "pre_add":
        pk = kwargs["pk_set"]       # get list of newly added heights
        new_res = AvailableHeight.objects.filter(pk__in=pk).values_list("height", flat=True)    # new heights
        for res in new_res:
            images = UploadedImage.objects.filter(parent=None, owner__tier=instance)     # all original images
            for img in images:
                # check if image has thumbnail with requested size (maybe user had that height available in previous tier and file already exists)
                if res not in img.uploadedimage_set.all().values_list("height", flat=True):
                    UploadedImage.objects.create(
                        image = get_resized_image(img.image, res),
                        owner = img.owner,
                        title = img.title,
                        parent = img,
                    )



m2m_changed.connect(signal, sender=Tier.available_heights.through)