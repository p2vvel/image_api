from distutils.command.upload import upload
from zoneinfo import available_timezones
from django.test import TestCase
from django.conf import settings
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from django.conf import settings
from api.models import UploadedImage, Tier, AvailableHeight
from django.core.cache import cache
import json

class TestBinaryImages(TestCase):
    """
    Test binary images
    """
    def setUp(self) -> None:
        self.tier = Tier.objects.create(name="Premium", binary_image=True)
        self.tier.available_heights.add(AvailableHeight.objects.create(height=400))
        self.tier.save()
        self.delilah = get_user_model().objects.create(username="delilah", email="delilah@example.com")
        self.delilah.set_password("1234")
        self.delilah.save()
        self.login_data = {"username": "delilah", "password": "1234"}
        self.client.login(**self.login_data)
        test_image_dir = settings.BASE_DIR / "test_images"
        image = "cat1.jpg"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        # self.assertEqual(response.status_code, 200)

    def test_access_basic_generation(self):
        """
        Test access for user with and without proper tier
        """
        uploaded_image = UploadedImage.objects.get(height=200)

        response = self.client.get(reverse("generate_binary_link", args=(uploaded_image.image.name,)))   
        self.assertEqual(response.status_code, 403)     # no access - basic tier

    def test_access_tier_generation(self):
        """
        Test access for user with proper tier
        """
        uploaded_image = UploadedImage.objects.get(height=200)

        self.delilah.tier = self.tier
        self.delilah.save()

        response = self.client.get(reverse("generate_binary_link", args=(uploaded_image.image.name,)))   
        self.assertEqual(response.status_code, 200)     # no access - basic tier


    def test_anonymous_generation(self):
        """
        Anonymous user shouldnt be able to access binary image
        """
        uploaded_image = UploadedImage.objects.get(height=200)

        self.client.logout()

        response = self.client.get(reverse("generate_binary_link", args=(uploaded_image.image.name,)))   
        self.assertEqual(response.status_code, 403)     # no access - basic tier

    def test_token_generation(self):
        """
        Test if token appears after visiting generation view
        """
        uploaded_image = UploadedImage.objects.get(height=200)
        self.delilah.tier = self.tier
        self.delilah.save()

        response = self.client.get(reverse("generate_binary_link", args=(uploaded_image.image.name,)))   
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)["binary_image"].split("/")[-1]
        self.assertEqual(cache.get(token), uploaded_image.image.name)   # image name is stored in cache


    def test_binary_image_fetch_owner(self):
        """
        Test if binary image can be dowloaded by owner
        """
        uploaded_image = UploadedImage.objects.get(height=200)
        self.delilah.tier = self.tier
        self.delilah.save()

        response = self.client.get(reverse("generate_binary_link", args=(uploaded_image.image.name,)))   
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)["binary_image"].split("/")[-1]
        self.assertEqual(cache.get(token), uploaded_image.image.name)   # image name is stored in cache

        response = self.client.get(reverse("get_binary_image", args=(token,)))
        self.assertEqual(response.status_code, 200)     # owner can fetch binary image


    def test_binary_image_fetch_non_owner(self):
        """
        Test if binary image can be dowloaded by user that is not an owner
        """
        uploaded_image = UploadedImage.objects.get(height=200)
        self.delilah.tier = self.tier
        self.delilah.save()

        response = self.client.get(reverse("generate_binary_link", args=(uploaded_image.image.name,)))   
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)["binary_image"].split("/")[-1]
        self.assertEqual(cache.get(token), uploaded_image.image.name)   # image name is stored in cache

        self.client.logout()
        new_user = get_user_model().objects.create(username="fake_delilah", email="fake_delilah@example.com")
        new_user.set_password("1234")
        new_user.save()
        self.client.login(username="fake_delilah", password="1234")

        response = self.client.get(reverse("get_binary_image", args=(token,)))
        self.assertEqual(response.status_code, 403)     # non-owner can't fetch binary image


    def test_binary_image_fetch_anonymous(self):
        """
        Test if binary image can be dowloaded by anonymous user
        """
        uploaded_image = UploadedImage.objects.get(height=200)
        self.delilah.tier = self.tier
        self.delilah.save()

        response = self.client.get(reverse("generate_binary_link", args=(uploaded_image.image.name,)))   
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)["binary_image"].split("/")[-1]
        self.assertEqual(cache.get(token), uploaded_image.image.name)   # image name is stored in cache

        self.client.logout()

        response = self.client.get(reverse("get_binary_image", args=(token,)))
        self.assertEqual(response.status_code, 403)     # anonymous user can't fetch binary image


    def test_binary_image_expiration(self):
        """
        Test if binary image is available after expiration time (shouldn't be available)
        """
        uploaded_image = UploadedImage.objects.get(height=200)
        self.delilah.tier = self.tier
        self.delilah.save()

        response = self.client.get(reverse("generate_binary_link", args=(uploaded_image.image.name,)))   
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)["binary_image"].split("/")[-1]
        self.assertEqual(cache.get(token), uploaded_image.image.name)   # image name is stored in cache

        cache.touch(token, 0)       # simulate time expiration by settings TTL=0[s]

        response = self.client.get(reverse("get_binary_image", args=(token,)))
        self.assertEqual(response.status_code, 404)     # unavailable
