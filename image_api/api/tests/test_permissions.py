from django.test import TestCase
from django.conf import settings
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from django.conf import settings
from api.models import UploadedImage, Tier, AvailableHeight



class TestThumbnails(TestCase):
    """
    Test permissions, including tiers and ownership
    """
    def setUp(self) -> None:
        # self.tier = Tier.objects.create(name="Premium")
        # self.tier.available_heights.add(AvailableHeight.objects.create(height=400))
        # self.tier.save()
        self.delilah = get_user_model().objects.create(username="delilah", email="delilah@example.com")
        self.delilah.set_password("1234")
        self.delilah.save()
        self.login_data = {"username": "delilah", "password": "1234"}


    def test_basic_tier(self):
        """
        Test if user can always download 200px
        """
        self.client.login(**self.login_data)

        test_image_dir = settings.BASE_DIR / "test_images"
        image = "cat1.jpg"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)         # 403 = forbidden
        
        px200 = UploadedImage.objects.get(height=200)
        response = self.client.get(reverse("get_image", args=(px200.image.name, )))
        self.assertEqual(response.status_code, 200)     # 200px thumbnail should be available

        original = UploadedImage.objects.get(parent=None)
        response = self.client.get(reverse("get_image", args=(original.image.name, )))
        self.assertEqual(response.status_code, 403)     # original image should be unavailable

    def test_custom_tier(self):
        """
        Test if user can download custom resolutions and original image
        """
        self.client.login(**self.login_data)
        tier = Tier.objects.create(name="Premium")
        tier.original_image = True
        tier.available_heights.add(AvailableHeight.objects.create(height=400))
        tier.available_heights.add(AvailableHeight.objects.create(height=800))
        tier.save()
        
        self.delilah.tier = tier
        self.delilah.save()

        test_image_dir = settings.BASE_DIR / "test_images"
        image = "cat1.jpg"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)         # 403 = forbidden
        
        for res in [200, 400, 800]:
            thumbnail = UploadedImage.objects.get(height=res)
            response = self.client.get(reverse("get_image", args=(thumbnail.image.name, )))
            self.assertEqual(response.status_code, 200)     # thumbnails should be available

        original = UploadedImage.objects.get(parent=None)
        response = self.client.get(reverse("get_image", args=(original.image.name, )))
        self.assertEqual(response.status_code, 200)     # original image should be available


    def test_anonymous_access(self):
        """
        Test what happens if user changes tier
        """
        self.client.login(**self.login_data)
        tier = Tier.objects.create(name="Premium")
        tier.original_image = True
        tier.available_heights.add(AvailableHeight.objects.create(height=400))
        tier.available_heights.add(AvailableHeight.objects.create(height=800))
        tier.save()
        
        self.delilah.tier = tier
        self.delilah.save()

        test_image_dir = settings.BASE_DIR / "test_images"
        image = "cat1.jpg"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)         # 403 = forbidden
        
        for res in [200, 400, 800]:
            thumbnail = UploadedImage.objects.get(height=res)
            response = self.client.get(reverse("get_image", args=(thumbnail.image.name, )))
            self.assertEqual(response.status_code, 200)     # thumbnails should be available

        original = UploadedImage.objects.get(parent=None)
        response = self.client.get(reverse("get_image", args=(original.image.name, )))
        self.assertEqual(response.status_code, 200)     # original image should be available

        self.delilah.tier = None    # tier change
        self.delilah.save()

        for res in [400, 800]:
            thumbnail = UploadedImage.objects.get(height=res)
            response = self.client.get(reverse("get_image", args=(thumbnail.image.name, )))
            self.assertEqual(response.status_code, 403)     # thumbnails should be unavailable

        original = UploadedImage.objects.get(parent=None)
        response = self.client.get(reverse("get_image", args=(original.image.name, )))
        self.assertEqual(response.status_code, 403)     # original image should be available


    def test_anonymous_access(self):
        """
        Anonymous user shouldn't have any access
        """
        self.client.login(**self.login_data)
        tier = Tier.objects.create(name="Premium")
        tier.original_image = True
        tier.available_heights.add(AvailableHeight.objects.create(height=400))
        tier.available_heights.add(AvailableHeight.objects.create(height=800))
        tier.save()
        
        self.delilah.tier = tier
        self.delilah.save()

        test_image_dir = settings.BASE_DIR / "test_images"
        image = "cat1.jpg"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        for res in [200, 400, 800]:
            thumbnail = UploadedImage.objects.get(height=res)
            response = self.client.get(reverse("get_image", args=(thumbnail.image.name, )))
            self.assertEqual(response.status_code, 200)     # thumbnails should be available

        original = UploadedImage.objects.get(parent=None)
        response = self.client.get(reverse("get_image", args=(original.image.name, )))
        self.assertEqual(response.status_code, 200)     # original image should be available
        
        self.client.logout()
        
        for res in [200, 400, 800]:
            thumbnail = UploadedImage.objects.get(height=res)
            response = self.client.get(reverse("get_image", args=(thumbnail.image.name, )))
            self.assertEqual(response.status_code, 403)

        original = UploadedImage.objects.get(parent=None)
        response = self.client.get(reverse("get_image", args=(original.image.name, )))
        self.assertEqual(response.status_code, 403)

    def test_non_owner(self):
        """
        Users shouldn't be able to see each others images
        """
        self.client.login(**self.login_data)
        tier = Tier.objects.create(name="Premium")
        tier.original_image = True
        tier.available_heights.add(AvailableHeight.objects.create(height=400))
        tier.available_heights.add(AvailableHeight.objects.create(height=800))
        tier.save()
        
        self.delilah.tier = tier
        self.delilah.save()

        test_image_dir = settings.BASE_DIR / "test_images"
        image = "cat1.jpg"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        for res in [200, 400, 800]:
            thumbnail = UploadedImage.objects.get(height=res)
            response = self.client.get(reverse("get_image", args=(thumbnail.image.name, )))
            self.assertEqual(response.status_code, 200)     # thumbnails should be available

        original = UploadedImage.objects.get(parent=None)
        response = self.client.get(reverse("get_image", args=(original.image.name, )))
        self.assertEqual(response.status_code, 200)     # original image should be available
        

        self.client.logout()
        new_user = get_user_model().objects.create(username="fake_delilah", email="fake_delilah@example.com")
        new_user.set_password("1234")
        new_user.save()
        self.client.login(username="fake_delilah", password="1234")
        
        for res in [200, 400, 800]:
            thumbnail = UploadedImage.objects.get(height=res)
            response = self.client.get(reverse("get_image", args=(thumbnail.image.name, )))
            self.assertEqual(response.status_code, 403)

        original = UploadedImage.objects.get(parent=None)
        response = self.client.get(reverse("get_image", args=(original.image.name, )))
        self.assertEqual(response.status_code, 403)
