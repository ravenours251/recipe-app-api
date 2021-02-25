from core.models import Ingredient
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .. import serializers

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicApiIngredient(TestCase):
    """ Test if the Ingredient API is publicly available"""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email='wiwe@gmail.com',
            password='Signup!23'
        )

        self.client = APIClient()

    def test_api_need_authenticate(self):
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApiIngredient(TestCase):
    """ Test private api END POINT"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='wiwe@gmail.com',
            password='Signup!23'
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_list(self):
        Ingredient.objects.create(user=self.user, name='Milk')
        Ingredient.objects.create(user=self.user, name='Cow')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = serializers.IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that only ingredients for authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@ravenours.com',
            'password!23'
        )
        Ingredient.objects.create(user=user2, name='Vinegar')

        ingredients = Ingredient.objects.create(user=self.user, name='Toyo')
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredients.name)

    def test_create_ingredient_successful(self):
        """ Test if the ingredient object created succesffully"""

        payload = {'name': 'Cabbe'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
            ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """ Test creating a blank Ingredient"""
        payload = {'name': ''}

        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
