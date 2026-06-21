# main.py (Simplified Windows Version)
import os
import sys
import time
import getpass
import logging
import platform
from datetime import datetime

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except:
    # If colorama is not installed, define dummy colors
    class Fore:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
    
    class Style:
        BRIGHT = '\033[1m'
        RESET_ALL = '\033[0m'

from config import Config
from crypto_engine import CryptoEngine
from usb_manager_windows import USBManager
from file_manager import FileManager

class CipherDriveApp:
    def __init__(self):
        self.config = Config()
        self.usb_manager = USBManager()
        self.crypto_engine = None
        self.file_manager = None
        self.setup_logging()
        self.running = True
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cipher_drive.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('CipherDrive')
    
    def display_banner(self):
        """Display application banner"""
        banner = f"""
{Fore.CYAN}
    {Fore.YELLOW} Cipher Drive - Secure USB Management System{Fore.CYAN}     


{Fore.GREEN} Auto-Detecting | Cryptographically Protected | USB Manager

{Fore.WHITE}Press Ctrl+C to exit
"""
        print(banner)
    
    def setup_master_password(self):
        """Setup master password for encryption"""
        if not os.path.exists(self.config.get_key_path()):
            print(f"{Fore.YELLOW} First time setup - Create master key")
            password = getpass.getpass("Enter master password: ")
            confirm = getpass.getpass("Confirm master password: ")
            
            if password != confirm:
                print(f"{Fore.RED} Passwords do not match!")
                return False
            
            self.crypto_engine = CryptoEngine(password)
            key_path = self.config.get_key_path()
            self.crypto_engine.generate_key_file(key_path)
            print(f"{Fore.GREEN} Master key created successfully!")
            return True
        else:
            password = getpass.getpass("Enter master password: ")
            self.crypto_engine = CryptoEngine(password)
            try:
                key_path = self.config.get_key_path()
                self.crypto_engine.load_key_file(key_path)
                print(f"{Fore.GREEN} Authentication successful!")
                return True
            except Exception as e:
                print(f"{Fore.RED} Authentication failed: {e}")
                return False
    
    def usb_callback(self, device):
        """Callback when new USB device is detected"""
        print(f"\n{Fore.GREEN} New USB device detected: {device['device']}")
        print(f"   Mount point: {device.get('mountpoint', 'N/A')}")
        
        if 'total' in device:
            size = device['total']
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    size_str = f"{size:.2f} {unit}"
                    break
                size /= 1024.0
            else:
                size_str = f"{size:.2f} TB"
            print(f"   Size: {size_str}")
        
        print(f"\n{Fore.CYAN}Options:")
        print("  1. Encrypt all files on device")
        print("  2. Decrypt all files on device")
        print("  3. View device info")
        print("  4. Skip")
        
        choice = input(f"{Fore.WHITE}Select option (1-4): ").strip()
        
        if choice == '1':
            self.encrypt_usb_device(device)
        elif choice == '2':
            self.decrypt_usb_device(device)
        elif choice == '3':
            self.show_device_info(device)
        else:
            print(f"{Fore.YELLOW} Skipping device")
    
    def encrypt_usb_device(self, device):
        """Encrypt all files on USB device"""
        mount_point = device.get('mountpoint')
        if not mount_point:
            print(f"{Fore.RED} No mount point available")
            return
        
        print(f"{Fore.YELLOW} Encrypting files on {mount_point}...")
        
        try:
            self.file_manager = FileManager(self.crypto_engine)
            results = self.file_manager.process_files(mount_point, auto_decrypt=False)
            print(f"\n{Fore.GREEN} Encryption complete!")
            print(f"   Processed: {len(results['processed'])} files")
            print(f"   Errors: {len(results['errors'])}")
        except Exception as e:
            print(f"{Fore.RED} Encryption failed: {e}")
    
    def decrypt_usb_device(self, device):
        """Decrypt all files on USB device"""
        mount_point = device.get('mountpoint')
        if not mount_point:
            print(f"{Fore.RED} No mount point available")
            return
        
        print(f"{Fore.YELLOW} Decrypting files on {mount_point}...")
        
        try:
            self.file_manager = FileManager(self.crypto_engine)
            results = self.file_manager.process_files(mount_point, auto_decrypt=True)
            print(f"\n{Fore.GREEN} Decryption complete!")
            print(f"   Processed: {len(results['processed'])} files")
            print(f"   Errors: {len(results['errors'])}")
        except Exception as e:
            print(f"{Fore.RED} Decryption failed: {e}")
    
    def show_device_info(self, device):
        """Display detailed device information"""
        print(f"\n{Fore.CYAN} Device Information:")
        print(f"   Device: {device.get('device', 'N/A')}")
        print(f"   Mount Point: {device.get('mountpoint', 'N/A')}")
        print(f"   File System: {device.get('fstype', 'N/A')}")
        print(f"   Options: {device.get('opts', 'N/A')}")
        
        if 'total' in device:
            size = device['total']
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    print(f"   Total Space: {size:.2f} {unit}")
                    break
                size /= 1024.0
        
        if 'used' in device:
            size = device['used']
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    print(f"   Used Space: {size:.2f} {unit}")
                    break
                size /= 1024.0
        
        if 'free' in device:
            size = device['free']
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    print(f"   Free Space: {size:.2f} {unit}")
                    break
                size /= 1024.0
        
        if 'percent' in device:
            print(f"   Usage: {device['percent']:.1f}%")
    
    def interactive_menu(self):
        """Interactive menu for manual operations"""
        while True:
            print(f"\n{Fore.CYAN} Main Menu:")
            print("  1. Monitor USB devices")
            print("  2. Manually encrypt a directory")
            print("  3. Manually decrypt a directory")
            print("  4. Create secure backup")
            print("  5. View logs")
            print("  6. Exit")
            
            choice = input(f"{Fore.WHITE}Select option (1-6): ").strip()
            
            if choice == '1':
                self.start_usb_monitoring()
            elif choice == '2':
                self.manual_encrypt()
            elif choice == '3':
                self.manual_decrypt()
            elif choice == '4':
                self.create_backup()
            elif choice == '5':
                self.view_logs()
            elif choice == '6':
                self.exit_application()
                break
            else:
                print(f"{Fore.RED} Invalid option")
    
    def start_usb_monitoring(self):
        """Start USB monitoring"""
        print(f"{Fore.GREEN}🔍 Starting USB monitoring...")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop monitoring")
        print(f"{Fore.YELLOW}Insert a USB drive to test detection")
        
        try:
            self.usb_manager.detect_new_device(self.usb_callback)
            
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW} Stopping USB monitoring...")
            self.usb_manager.stop_monitoring()
    
    def manual_encrypt(self):
        """Manual encryption of a directory"""
        directory = input(f"{Fore.WHITE}Enter directory path to encrypt: ").strip()
        
        if not os.path.exists(directory):
            print(f"{Fore.RED} Directory does not exist")
            return
        
        print(f"{Fore.YELLOW} Encrypting files in {directory}...")
        
        try:
            self.file_manager = FileManager(self.crypto_engine)
            results = self.file_manager.process_files(directory, auto_decrypt=False)
            print(f"\n{Fore.GREEN} Encryption complete!")
            print(f"   Processed: {len(results['processed'])} files")
            print(f"   Errors: {len(results['errors'])}")
        except Exception as e:
            print(f"{Fore.RED} Encryption failed: {e}")
    
    def manual_decrypt(self):
        """Manual decryption of a directory"""
        directory = input(f"{Fore.WHITE}Enter directory path to decrypt: ").strip()
        
        if not os.path.exists(directory):
            print(f"{Fore.RED} Directory does not exist")
            return
        
        print(f"{Fore.YELLOW} Decrypting files in {directory}...")
        
        try:
            self.file_manager = FileManager(self.crypto_engine)
            results = self.file_manager.process_files(directory, auto_decrypt=True)
            print(f"\n{Fore.GREEN} Decryption complete!")
            print(f"   Processed: {len(results['processed'])} files")
            print(f"   Errors: {len(results['errors'])}")
        except Exception as e:
            print(f"{Fore.RED} Decryption failed: {e}")
    
    def create_backup(self):
        """Create encrypted backup of a directory"""
        source = input(f"{Fore.WHITE}Enter source directory: ").strip()
        backup_dir = input(f"{Fore.WHITE}Enter backup destination: ").strip()
        
        if not os.path.exists(source):
            print(f"{Fore.RED} Source directory does not exist")
            return
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        print(f"{Fore.YELLOW} Creating encrypted backup...")
        
        try:
            self.file_manager = FileManager(self.crypto_engine)
            backup_path = self.file_manager.create_secure_backup(source, backup_dir)
            print(f"{Fore.GREEN} Backup created successfully!")
            print(f"   Location: {backup_path}")
        except Exception as e:
            print(f"{Fore.RED} Backup failed: {e}")
    
    def view_logs(self):
        """Display application logs"""
        log_file = 'cipher_drive.log'
        
        if not os.path.exists(log_file):
            print(f"{Fore.YELLOW} No log file found")
            return
        
        print(f"{Fore.CYAN} Recent logs:")
        print("-" * 60)
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-20:]:
                    print(line.strip())
        except Exception as e:
            print(f"{Fore.RED} Error reading logs: {e}")
    
    def exit_application(self):
        """Clean exit of application"""
        print(f"\n{Fore.GREEN} Shutting down Cipher Drive...")
        if self.usb_manager.monitoring:
            self.usb_manager.stop_monitoring()
        self.running = False
        print(f"{Fore.CYAN} Cipher Drive shutdown complete")
    
    def run(self):
        """Main application entry point"""
        self.display_banner()
        
        if not self.setup_master_password():
            print(f"{Fore.RED} Setup failed. Exiting...")
            sys.exit(1)
        
        self.interactive_menu()

def main():
    try:
        app = CipherDriveApp()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW} Application interrupted by user")
    except Exception as e:
        print(f"{Fore.RED} Unexpected error: {e}")
        logging.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        print(f"{Fore.CYAN} Goodbye!")

if __name__ == "__main__":
    main()