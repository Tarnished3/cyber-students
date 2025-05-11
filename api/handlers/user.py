from tornado.web import authenticated
from .auth import AuthHandler
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64decode

# Decryption 
def decrypt_field(key, encrypted_obj):
    iv = bytes.fromhex(encrypted_obj['iv'])
    ciphertext = bytes.fromhex(encrypted_obj['ciphertext'])
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


class UserHandler(AuthHandler):

    @authenticated
    def get(self):
        self.set_status(200)
        self.response['email'] = self.current_user['email']


        key = os.environ.get("ENCRYPTION_KEY")
        

        key = key.encode()
        if len(key) != 32:


            self.send_error(500, message='Invalid length.')
            return

        encrypted_fields = user.get('encrypted_fields', {})
        try:
            decrypted_fields = {
                'full_name': decrypt_field(key, encrypted_fields['full_name']).decode(),
                'displayName': decrypt_field(key, encrypted_fields['display_name']).decode(),
                'address': decrypt_field(key, encrypted_fields['address']).decode(),
                'date_of_birth': decrypt_field(key, encrypted_fields['date_of_birth']).decode(),
                'phone_number': decrypt_field(key, encrypted_fields['phone_number']).decode(),
                'disabilities': decrypt_field(key, encrypted_fields['disabilities']).decode().split(',') 
            }
        except Exception as e:
            self.send_error(500, message='Decryption failed.')
            return

        self.set_status(200)
        self.response = {
            'email': user['email'],
            **decrypted_fields
        }
        self.write_json()



     