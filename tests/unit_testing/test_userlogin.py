from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from web.apps.web_copo.models import User
from faker import Faker


from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class UserSignUpTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_object = UserFactory.build()
        cls.user_saved = UserFactory.create()
        cls.client = APIClient()
        cls.signup_url = reverse('rest_register')
        cls.faker_obj = Faker()

    def test_if_data_is_correct_then_signup(self):
        # Prepare data
        signup_dict = {
            'username': self.user_object.username,
            'password1': 'test_Pass',
            'password2': 'test_Pass',
            'phone_number': self.user_object.phone_number,
            'category': self.user_object.category,
        }
        # Make request
        response = self.client.post(self.signup_url, signup_dict)
        # Check status response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        # Check database
        new_user = User.objects.get(username=self.user_object.username)
        self.assertEqual(
            new_user.category,
            self.user_object.category,
        )
        self.assertEqual(
            new_user.phone_number,
            self.user_object.phone_number,
        )

    def test_if_username_already_exists_dont_signup(self):
        # Prepare data with already saved user
        signup_dict = {
            'username': self.user_saved.username,
            'password1': 'test_Pass',
            'password2': 'test_Pass',
            'phone_number': self.user_saved.phone_number,
            'category': self.user_saved.category,
        }
        # Make request
        response = self.client.post(self.signup_url, signup_dict)
        # Check status response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['username'][0]),
            'A user with that username already exists.',
        )
        # Check database
        # Check that there is only one user with the saved username
        username_query = User.objects.filter(username=self.user_saved.username)
        self.assertEqual(username_query.count(), 1)

    def test_update_email(self):
        pk = "1"
        data = {
            "name": "Mercedes Benz"
        }

        response = self.client.patch(self.url + f"/{pk}", data=data)
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["name"], "Mercedes Benz")

class UserLoginTestCase(APITestCase):

    @classmethod
    def setUp(self):
        # SetUp required environment for tests
        self.client = APIClient()
        self.user = User(first_name='test_user', last_name='test', email=
        'test@gmail.com', username='test', password="abc123")
        self.user.set_password("abc123")
        self.user.save()
        self.token = Token.objects.create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_user_login(self):
        data = {'username': 'test', 'password': "abc123"}
        login_url = reverse('login')

        response = self.client.post(login_url, data)
        resp = response.json()
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        # Clean up after each test
        self.user.delete()