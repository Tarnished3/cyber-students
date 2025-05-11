import os
from json import dumps
from tornado.escape import json_decode
from tornado.web import Application
from api.handlers.registration import RegistrationHandler
from .base import BaseTest

class RegistrationHandlerTest(BaseTest):

    @classmethod
    def setUpClass(cls):
        os.environ['ENCRYPTION_KEY'] = 'a' * 32 
        cls.my_app = Application([(r'/registration', RegistrationHandler)])
        super().setUpClass()

    def test_registration_with_all_fields(self):
        body = {
            'email': 'test1@example.com',
            'password': 'securePassword123',
            'displayName': 'TestUser',
            'full_name': 'Test User',
            'address': '123 Test St',
            'date_of_birth': '1990-01-01',
            'phone_number': '+1234567890',
            'disabilities': ['visual', 'mobility']
        }

        response = self.fetch('/registration', method='POST', body=dumps(body))
        self.assertEqual(200, response.code)

        response_data = json_decode(response.body)
        self.assertEqual(response_data['email'], body['email'])

    def test_registration_without_display_name_defaults_to_email(self):
        email = 'test2@example.com'
        body = {
            'email': email,
            'password': 'TestPass2'
        }

        response = self.fetch('/registration', method='POST', body=dumps(body))
        self.assertEqual(200, response.code)

        response_data = json_decode(response.body)
        self.assertEqual(response_data['email'], email)

    def test_missing_encryption_key(self):
        del os.environ['ENCRYPTION_KEY']
        body = {
            'email': 'fail@example.com',
            'password': 'fail',
            'displayName': 'FailUser'
        }

        response = self.fetch('/registration', method='POST', body=dumps(body))
        self.assertEqual(response.code, 500)

        response1 = self.fetch('/registration', method='POST', body=dumps(body))
        self.assertEqual(response1.code, 200)

        response2 = self.fetch('/registration', method='POST', body=dumps(body))
        self.assertEqual(response2.code, 409)
