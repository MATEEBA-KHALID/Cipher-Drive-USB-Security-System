# file_manager.py
import os
import shutil
import hashlib
import time
from datetime import datetime
import logging

class FileManager:
    def __init__(self, crypto_engine):
        self.crypto_engine = crypto_engine
        self.processed_files = set()
        self.logger = logging.getLogger('FileManager')
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get_file_hash(self, file_path, block_size=65536):
        """Calculate file hash for integrity verification"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                sha256.update(block)
        return sha256.hexdigest()
    
    def process_files(self, directory, auto_decrypt=True):
        """Process files in a directory"""
        results = {
            'processed': [],
            'errors': [],
            'skipped': []
        }
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip already processed files
                if file_path in self.processed_files:
                    continue
                
                try:
                    # Process based on file extension
                    if file.endswith('.cipher') and auto_decrypt:
                        # Encrypted file - decrypt
                        output_file = self.crypto_engine.decrypt_file(file_path)
                        os.remove(file_path)  # Remove encrypted file after decryption
                        results['processed'].append({
                            'file': file_path,
                            'action': 'decrypted',
                            'output': output_file
                        })
                        self.processed_files.add(file_path)
                    
                    elif not file.endswith('.cipher') and not auto_decrypt:
                        # Unencrypted file - encrypt
                        output_file = self.crypto_engine.encrypt_file(file_path)
                        os.remove(file_path)  # Remove original file after encryption
                        results['processed'].append({
                            'file': file_path,
                            'action': 'encrypted',
                            'output': output_file
                        })
                        self.processed_files.add(file_path)
                    
                    else:
                        results['skipped'].append(file_path)
                        
                except Exception as e:
                    results['errors'].append({
                        'file': file_path,
                        'error': str(e)
                    })
                    self.logger.error(f"Error processing {file_path}: {e}")
        
        return results
    
    def create_secure_backup(self, source_dir, backup_dir):
        """Create encrypted backup of directory"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'backup_{timestamp}')
        os.makedirs(backup_path, exist_ok=True)
        
        # Copy files and encrypt
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(src_file, source_dir)
                dst_file = os.path.join(backup_path, rel_path)
                
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                self.crypto_engine.encrypt_file(src_file, dst_file + '.cipher')
        
        return backup_path
    
    def verify_file_integrity(self, original_file, encrypted_file, decrypted_file):
        """Verify file integrity through hash comparison"""
        try:
            # Calculate hashes
            original_hash = self.get_file_hash(original_file)
            decrypted_hash = self.get_file_hash(decrypted_file)
            
            return original_hash == decrypted_hash
        except Exception as e:
            self.logger.error(f"Integrity verification failed: {e}")
            return False
    
    def cleanup_temp_files(self, directory, pattern='*.tmp'):
        """Clean up temporary files"""
        import glob
        
        temp_files = glob.glob(os.path.join(directory, pattern))
        for file in temp_files:
            try:
                os.remove(file)
                self.logger.info(f"Removed temporary file: {file}")
            except Exception as e:
                self.logger.error(f"Failed to remove {file}: {e}")
    
    def get_file_info(self, file_path):
        """Get detailed file information"""
        try:
            stat = os.stat(file_path)
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stat.st_size,
                'size_human': self.human_readable_size(stat.st_size),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'hash': self.get_file_hash(file_path) if os.path.isfile(file_path) else None
            }
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return None
    
    @staticmethod
    def human_readable_size(size):
        """Convert size to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"