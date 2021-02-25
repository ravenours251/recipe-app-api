from django.test import TestCase
from django.contrib.auth import get_user_model
from .. import models


def sample_user(email='test@ravenours.com', password='Signup!23'):
    """ Create a sample user """
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        """ Test creating a new user with an email is successful"""
        email = 'joshua@ravenours.com'
        password = 'Signup!23'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_normalize_email(self):
        """ Test email if lower case"""
        email = 'joshua@RAVENOURS.com'
        user = get_user_model().objects.create_user(email, 'Testpassword!23')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test Creating User with no email error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'password!@#')

    def test_create_new_superuser(self):
        """ Test for creating new super user"""
        user = get_user_model().objects.create_superuser(
            'test12@gmail.com',
            'testpassword'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """ Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Ochia'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingd_str(self):
        """Test the ingridients str representation """
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
            )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe(self):
        """ Test recipe str representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak & mushroom',
            time_minute=5,
            price=5.00,
        )

        self.assertEqual(str(recipe), recipe.title)
