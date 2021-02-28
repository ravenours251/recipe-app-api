from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .. import serializers
from core.models import Ingredient, Recipe

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

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Apple'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Banana'
        )
        recipe = Recipe.objects.create(
            title='Apple shit',
            time_minute=30,
            price=30.00,
            user=self.user
        )
        recipe.ingredient.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        serializer1 = serializers.IngredientSerializer(ingredient1)
        serializer2 = serializers.IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredient_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""

        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Potangina'
            )
        Ingredient.objects.create(user=self.user, name='Cheese')
        recipe1 = Recipe.objects.create(
            title='Eggs benedict',
            time_minute=30,
            price=12.00,
            user=self.user
        )
        recipe1.ingredient.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='Green eggs on toast',
            time_minute=20,
            price=5.00,
            user=self.user
        )
        recipe2.ingredient.add(ingredient)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
