from django.db.models.signals import pre_save
from django.dispatch import receiver

# these signals aren't universal, so no need to use get_user_model():
from api.models import User     



@receiver(pre_save, sender=User)
def my_handler(sender, instance, **kwargs):
    """
    Signal created to handle tier change.

    Images are created at upload, so when changing tier, or creating the new one,
    there would be a problem, because there wouldn't be all sizes of thumbnails.
    I detect tier change, and generate new, proper size thumbnails, to provide all sizes to user
    """
    if instance.tier:
        instance.old_thumbnail_sizes = instance.tier.extra_image_sizes    # save old thumbnail sizes
    else:
        instance.old_thumbnail_sizes = []     # no tier - empty array