# utils.py
import os
import sys
import platform
import subprocess

def get_system_info():
    """Get system information"""
    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.machine(),
        'python_version': sys.version
    }

def check_dependencies():
    """Check if all required system dependencies are installed"""
    dependencies = {
        'mount': 'util-linux',
        'umount': 'util-linux'
    }
    
    missing = []
    for cmd, package in dependencies.items():
        if not shutil.which(cmd):
            missing.append(package)
    
    return missing

def secure_delete(file_path, passes=3):
    """Securely delete a file using multiple overwrite passes"""
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'rb+') as f:
            size = os.path.getsize(file_path)
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(size))
                f.flush()
        
        os.remove(file_path)
        return True
    except Exception as e:
        logging.error(f"Secure delete failed: {e}")
        return False