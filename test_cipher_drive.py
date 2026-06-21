# test_cipher_drive.py
import unittest
import os
import tempfile
from crypto_engine import CryptoEngine
from file_manager import FileManager

class TestCipherDrive(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.password = "test_password"
        self.crypto = CryptoEngine(self.password)
        self.file_manager = FileManager(self.crypto)
    
    def test_encryption_decryption(self):
        # Create test file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Encrypt
        encrypted = self.crypto.encrypt_file(test_file)
        self.assertTrue(os.path.exists(encrypted))
        
        # Decrypt
        decrypted = self.crypto.decrypt_file(encrypted)
        self.assertTrue(os.path.exists(decrypted))
        
        # Verify content
        with open(decrypted, 'r') as f:
            content = f.read()
        self.assertEqual(content, "Test content")
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

if __name__ == '__main__':
    unittest.main()