from json import dumps
from logging import info
from tornado.escape import json_decode, utf8
from tornado.gen import coroutine
from werkzeug.security import generate_password_hash
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from .base import BaseHandler
from ..conf import ENCRYPTION_KEY

# Helper AEs
def encrypt_field(key, plaintext):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return {'iv': iv.hex(), 'ciphertext': ciphertext.hex()}

class RegistrationHandler(BaseHandler):

    @coroutine
    def post(self):
        try:
            body = json_decode(self.request.body)
            email = body['email'].lower().strip()
            password = body['password']
            full_name = body.get('full_name', '')
            display_name = body.get('displayName', email)
            address = body.get('address', '')
            date_of_birth = body.get('date_of_birth', '')
            phone_number = body.get('phone_number', '')
            disabilities = body.get('disabilities', [])

            if not isinstance(email, str) or not isinstance(password, str) or not isinstance(display_name, str):
                raise Exception()
        except Exception:
            self.send_error(400, message='You must provide a valid email, password, and display name!')
            return

        # Email checker
        existing_user = yield self.db.users.find_one({'email': email})
        if existing_user:
            self.send_error(409, message='A user with the given email address already exists!')
            return
        # insert encyption key
        key = ENCRYPTION_KEY
        if not key:
            self.send_error(500, message='Encryption key not set!')
            return
        key = key.encode()
        if len(key) != 32:
            self.send_error(500, message='Encryption key must be 32 bytes (AES-256).')
            return
        # Encrypt fields
        encrypted_fields = {
            'full_name': encrypt_field(key, full_name),
            'display_name': encrypt_field(key, display_name),
            'address': encrypt_field(key, address),
            'date_of_birth': encrypt_field(key, date_of_birth),
            'phone_number': encrypt_field(key, phone_number),
            'disabilities': encrypt_field(key, ','.join(disabilities))  # Join list into single string
        }
        # HAshing
        hashed_password = generate_password_hash(password)
        # encrypted user
        yield self.db.users.insert_one({
            'email': email,
            'password': hashed_password,
            'encrypted_fields': encrypted_fields
        })

        self.set_status(200)
        self.response['email'] = email
        self.write_json()
