from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTest(TestCase):
    """ Test public user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ Testing create user"""
        payload = {
            'email': 'gago@gmail.com',
            'password': 'Signup!23',
            'name': 'Joshua Macmod'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exist(self):
        """ Test creating user that already exist"""
        payload = {
            'email': 'gago@gmail.com',
            'password': 'Signup!23',
            'name': 'Joshua Macmod'
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Test that password is more than 5 char"""
        payload = {
            'email': 'gago@gmail.com',
            'password': 'pw',
            'name': 'Joshua Macmod'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exist = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """ Check if token is created for the user"""
        payload = {
            'email': 'gago@gmail.com',
            'password': 'Signup!23',
            'name': 'Joshua Macmod'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):

        create_user(email='joshua@wawei.com', password='wrong')
        payload = {
            'email': 'gago@gmail.com',
            'password': 'Signup!23',
            'name': 'Joshua Macmod'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_token_user(self):
        """Test that token is not create if user doesn't exit"""
        payload = {
            'email': 'gago@gmail.com',
            'password': 'Signup!23',
            'name': 'Joshua Macmod'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """ Test that email and password are required """
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
