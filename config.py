# config.py (Enhanced for GUI)
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Encryption settings
    ENCRYPTION_ALGORITHM = 'AES-256-GCM'
    KEY_DERIVATION_ITERATIONS = 100000
    SALT_SIZE = 32
    NONCE_SIZE = 12
    
    # USB settings
    USB_POLL_INTERVAL = 2  # seconds
    USB_TIMEOUT = 30  # seconds
    
    # File settings
    ALLOWED_EXTENSIONS = {'.txt', '.docx', '.pdf', '.jpg', '.png', '.mp4', '.zip'}
    MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
    ENCRYPTED_EXTENSION = '.cipher'
    
    # Logging
    LOG_FILE = 'cipher_drive_gui.log'
    LOG_LEVEL = 'INFO'
    
    # Security
    SESSION_TIMEOUT = 300  # 5 minutes
    MAX_RETRY_ATTEMPTS = 3
    
    # GUI Settings
    GUI_THEME = 'dark'
    GUI_FONT = 'Segoe UI'
    GUI_WINDOW_SIZE = '1000x700'
    
    @staticmethod
    def get_key_path():
        key_dir = os.path.join(os.path.expanduser('~'), '.cipher_drive')
        os.makedirs(key_dir, exist_ok=True)
        return os.path.join(key_dir, 'master.key')