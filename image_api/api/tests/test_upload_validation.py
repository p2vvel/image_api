from django.test import TestCase
from django.conf import settings
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from django.conf import settings
from api.models import UploadedImage



class TestUpload(TestCase):
    """
    Test upload and validation
    """
    def setUp(self) -> None:
        self.delilah = get_user_model().objects.create(username="delilah", email="delilah@example.com")
        self.delilah.set_password("1234")
        self.delilah.save()
        self.login_data = {"username": "delilah", "password": "1234"}

    def test_upload_anonymous(self):
        """
        Anonymous user shouldn't be able to upload anything
        """
        test_image_dir = settings.BASE_DIR / "test_images"
        image = "cat1.jpg"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 403)                                 # 403 = forbidden
        self.assertFalse(UploadedImage.objects.filter(title=image).count())         # entry created

    def test_jpg(self):
        """
        JPEGs should be uploadable
        """
        self.client.login(**self.login_data)
        test_image_dir = settings.BASE_DIR / "test_images"
        image = "cat1.jpg"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UploadedImage.objects.filter(title=image).count())      # entry created

    def test_png(self):
        """
        PNGs should be uploadable
        """
        self.client.login(**self.login_data)
        test_image_dir = settings.BASE_DIR / "test_images"
        image = "avatar1.png"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UploadedImage.objects.filter(title=image).count())      # entry created

    def test_gif(self):
        """
        Formats other than PNG and JPEG should be rejected on validation
        """
        self.client.login(**self.login_data)
        test_image_dir = settings.BASE_DIR / "test_images"
        image = "kiwka.gif"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 400)                             # 400 = validation error
        self.assertFalse(UploadedImage.objects.filter(title=image).count())     # entry wasnt created

    def test_bmp(self):
        """
        Formats other than PNG and JPEG should be rejected on validation
        """
        self.client.login(**self.login_data)
        test_image_dir = settings.BASE_DIR / "test_images"
        image = "klawier_cat.bmp"
        img = SimpleUploadedFile(image, open(test_image_dir / image, "rb").read())
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 400)                             # 400 = validation error
        self.assertFalse(UploadedImage.objects.filter(title=image).count())     # entry wasnt created

    def test_fake_jpeg(self):
        """
        Formats other than PNG and JPEG should be rejected on validation
        """
        self.client.login(**self.login_data)
        test_image_dir = settings.BASE_DIR / "test_images"
        image = "kiwka.gif"
        img = SimpleUploadedFile("kiwka.jpg", open(test_image_dir / image, "rb").read())    # sending fake .jpg file
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 400)                             # 400 = validation error
        self.assertFalse(UploadedImage.objects.filter(title=image).count())     # entry wasnt created

    def test_fake_png(self):
        """
        Formats other than PNG and JPEG should be rejected on validation
        """
        self.client.login(**self.login_data)
        test_image_dir = settings.BASE_DIR / "test_images"
        image = "klawier_cat.bmp"
        img = SimpleUploadedFile("klawier_cat.png", open(test_image_dir / image, "rb").read())    # sending fake .jpg file
        data = {"image": img}
        response = self.client.post(reverse("images-list"), data=data, follow=True)
        self.assertEqual(response.status_code, 400)                             # 400 = validation error
        self.assertFalse(UploadedImage.objects.filter(title=image).count())     # entry wasnt created