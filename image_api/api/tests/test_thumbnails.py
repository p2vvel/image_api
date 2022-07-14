from zoneinfo import available_timezones
from django.test import TestCase
from django.conf import settings
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from django.conf import settings
from api.models import UploadedImage, Tier, AvailableHeight



class TestThumbnails(TestCase):
    """
    Test upload and validation
    """
    def setUp(self) -> None:
        self.tier = Tier.objects.create(name="Premium")
        self.tier.available_heights.add(AvailableHeight.objects.create(height=400))
        self.tier.save()
        self.delilah = get_user_model().objects.create(username="delilah", email="delilah@example.com", tier=self.tier)
        self.delilah.set_password("1234")
        self.delilah.save()
        self.login_data = {"username": "delilah", "password": "1234"}


    def test_thumbnail_creation_base(self):
        """
        Thumbnails should be created at upload
        """
        self.client.login(**self.login_data)
        test_image_dir = settings.BASE_DIR / "test_images"
        image = "cat1.jpg"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)         # 403 = forbidden
        images = UploadedImage.objects.all()
        self.assertEqual(images.count(), 3)                 # original, 200px, 400px
        self.assertCountEqual([200, 400], [k.height for k in images.exclude(parent=None)])  # created thumbnails are 200px and 400px tall


    def test_thumbnail_creation_tier_change(self):
        """
        Thumbnails should be created at tier change
        """
        self.client.login(**self.login_data)
        test_image_dir = settings.BASE_DIR / "test_images"
        image = "cat1.jpg"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)         # 403 = forbidden
        images = UploadedImage.objects.all()
        self.assertEqual(images.count(), 3)                 # original, 200px, 400px
        self.assertCountEqual([200, 400], [k.height for k in images.exclude(parent=None)])  # created thumbnails are 200px and 400px tall

        tier = Tier.objects.create(name="Premium")
        tier.available_heights.add(AvailableHeight.objects.create(height=800))
        tier.save()
        self.delilah.tier = tier
        self.delilah.save()

        images = UploadedImage.objects.all()
        self.assertEqual(images.count(), 4)                 # original, 200px, 400px, 800px
        self.assertTrue(800 in [k.height for k in images.exclude(parent=None)])  # added 800px


    def test_thumbnail_creation_tier_extend(self):
        """
        Thumbnails should be created at tier extend
        """
        self.client.login(**self.login_data)
        test_image_dir = settings.BASE_DIR / "test_images"
        image = "cat1.jpg"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)         # 403 = forbidden
        images = UploadedImage.objects.all()
        self.assertEqual(images.count(), 3)                 # original, 200px, 400px
        self.assertCountEqual([200, 400], [k.height for k in images.exclude(parent=None)])  # created thumbnails are 200px and 400px tall

        self.tier.available_heights.add(AvailableHeight.objects.create(height=800))
        
        images = UploadedImage.objects.all()
        self.assertEqual(images.count(), 4)                 # original, 200px, 400px, 800px
        self.assertCountEqual([200, 400, 800], [k.height for k in images.exclude(parent=None)])  # 800px added
