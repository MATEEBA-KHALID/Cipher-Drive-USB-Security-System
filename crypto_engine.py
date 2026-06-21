# crypto_engine.py
import os
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from Crypto.Random import get_random_bytes
import json

class CryptoEngine:
    def __init__(self, password=None):
        self.password = password
        self.salt = None
        self.key = None
        self._derive_key()
    
    def _derive_key(self, salt=None):
        """Derive encryption key from password using PBKDF2"""
        if salt is None:
            self.salt = get_random_bytes(32)
        else:
            self.salt = salt
            
        if self.password:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
            )
            self.key = kdf.derive(self.password.encode())
    
    def encrypt_file(self, input_file, output_file=None):
        """Encrypt a file using AES-256-GCM"""
        if output_file is None:
            output_file = input_file + '.cipher'
            
        try:
            # Read file
            with open(input_file, 'rb') as f:
                plaintext = f.read()
            
            # Generate random nonce
            nonce = get_random_bytes(12)
            
            # Encrypt
            aesgcm = AESGCM(self.key)
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
            
            # Save encrypted data with metadata
            encrypted_data = {
                'salt': base64.b64encode(self.salt).decode(),
                'nonce': base64.b64encode(nonce).decode(),
                'ciphertext': base64.b64encode(ciphertext).decode()
            }
            
            with open(output_file, 'w') as f:
                json.dump(encrypted_data, f)
            
            return output_file
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_file(self, input_file, output_file=None):
        """Decrypt a file using AES-256-GCM"""
        if output_file is None:
            output_file = input_file.replace('.cipher', '')
        
        try:
            # Read encrypted data
            with open(input_file, 'r') as f:
                encrypted_data = json.load(f)
            
            # Extract components
            salt = base64.b64decode(encrypted_data['salt'])
            nonce = base64.b64decode(encrypted_data['nonce'])
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            
            # Re-derive key with stored salt
            self._derive_key(salt)
            
            # Decrypt
            aesgcm = AESGCM(self.key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            # Save decrypted file
            with open(output_file, 'wb') as f:
                f.write(plaintext)
            
            return output_file
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def encrypt_data(self, data):
        """Encrypt data in memory"""
        nonce = get_random_bytes(12)
        aesgcm = AESGCM(self.key)
        ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
        return {
            'salt': base64.b64encode(self.salt).decode(),
            'nonce': base64.b64encode(nonce).decode(),
            'ciphertext': base64.b64encode(ciphertext).decode()
        }
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data in memory"""
        salt = base64.b64decode(encrypted_data['salt'])
        nonce = base64.b64decode(encrypted_data['nonce'])
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        
        self._derive_key(salt)
        aesgcm = AESGCM(self.key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()
    
    def generate_key_file(self, key_path):
        """Generate and save master key"""
        key = get_random_bytes(32)
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        with open(key_path, 'wb') as f:
            f.write(key)
        return key
    
    def load_key_file(self, key_path):
        """Load master key from file"""
        with open(key_path, 'rb') as f:
            return f.read()