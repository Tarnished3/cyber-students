import os
from json import dumps
from base64 import b64encode
from tornado.escape import json_decode
from tornado.httputil import HTTPHeaders
from tornado.ioloop import IOLoop
from tornado.web import Application
from api.handlers.user import UserHandler
from .base import BaseTest
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from secrets import token_bytes

class UserHandlerTest(BaseTest):

    @classmethod
    def setUpClass(self):
        self.my_app = Application([(r'/user', UserHandler)])
        super().setUpClass()

    def encrypt_field(self, key, plaintext):
        iv = token_bytes(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        return {
            'iv': iv.hex(),
            'ciphertext': ciphertext.hex()
        }

    def setUp(self):
        super().setUp()
        self.key = os.urandom(32)
        os.environ["ENCRYPTION_KEY"] = self.key.decode('latin1') 
        self.email = 'test@test.com'
        self.password = 'testPassword'
        self.token = 'testToken'

        # Decrypt
        self.full_name = 'John Doe'
        self.display_name = 'jdoe'
        self.address = '123 Main St'
        self.dob = '2000-01-01'
        self.phone = '+1234567890'
        self.disabilities = ['vision', 'mobility']
        encrypted_fields = {
            'full_name': self.encrypt_field(self.key, self.full_name),
            'display_name': self.encrypt_field(self.key, self.display_name),
            'address': self.encrypt_field(self.key, self.address),
            'date_of_birth': self.encrypt_field(self.key, self.dob),
            'phone_number': self.encrypt_field(self.key, self.phone),
            'disabilities': self.encrypt_field(self.key, ','.join(self.disabilities)),
        }

        IOLoop.current().run_sync(lambda: self.get_app().db.users.insert_one({
            'email': self.email,
            'password': self.password,
            'token': self.token,
            'expiresIn': 2147483647,
            'encrypted_fields': encrypted_fields
        }))

 

def test_user_without_token(self):
        response = self.fetch('/user')
        self.assertEqual(400, response.code)

