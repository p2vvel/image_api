from django.test import TestCase
from django.conf import settings
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model


class TestApi(TestCase):
    # def test_image_upload(self):
        # self.assertTrue(True)

    def setUp(self) -> None:
        self.delilah = get_user_model().objects.create(username="delilah", email="delilah@example.com")
        self.delilah.set_password("1234")
        self.delilah.save()
        self.login_data = {"username": "delilah", "password": "1234"}


    def test_list_anonymous(self):
        """
        Anonymous user shouldn't have any access to the website
        """
        response = self.client.get(reverse("images-list"))
        self.assertEqual(response.status_code, 403)


    def test_list_logged(self):
        """
        Logged user has access
        """
        self.client.login(**self.login_data)
        response = self.client.get(reverse("images-list"))
        self.assertEqual(response.status_code, 200)

