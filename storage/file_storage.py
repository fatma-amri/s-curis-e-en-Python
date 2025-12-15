"""
File storage manager for handling file transfers.
"""

import os
import hashlib
from pathlib import Path
from utils.logger import SecureLogger
from utils.validators import validate_filename, validate_file_size

logger = SecureLogger('file_storage')


class FileStorage:
    """Manages file storage for transfers."""
    
    def __init__(self, files_directory='data/files'):
        """
        Initialize file storage.
        
        Args:
            files_directory: Directory for storing files
        """
        self.files_directory = files_directory
        Path(files_directory).mkdir(parents=True, exist_ok=True)
    
    def save_received_file(self, filename, file_data, peer_fingerprint):
        """
        Save a received file.
        
        Args:
            filename: Original filename
            file_data: File content bytes
            peer_fingerprint: Sender's fingerprint
            
        Returns:
            str: Path to saved file
        """
        # Validate filename
        if not validate_filename(filename):
            raise ValueError("Invalid filename")
        
        # Validate file size
        if not validate_file_size(len(file_data)):
            raise ValueError("File too large")
        
        # Create peer-specific directory
        peer_dir = os.path.join(self.files_directory, peer_fingerprint[:16])
        Path(peer_dir).mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = os.path.join(peer_dir, filename)
        
        # Avoid overwriting - add number suffix if needed
        counter = 1
        while os.path.exists(file_path):
            name, ext = os.path.splitext(filename)
            file_path = os.path.join(peer_dir, f"{name}_{counter}{ext}")
            counter += 1
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        logger.info(f"Saved file: {filename}", event="file_save")
        return file_path
    
    def prepare_file_for_sending(self, file_path):
        """
        Prepare a file for sending.
        
        Args:
            file_path: Path to file
            
        Returns:
            tuple: (filename, file_size, file_hash, file_data)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found")
        
        filename = os.path.basename(file_path)
        
        # Validate filename
        if not validate_filename(filename):
            raise ValueError("Invalid filename")
        
        # Read file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        file_size = len(file_data)
        
        # Validate size
        if not validate_file_size(file_size):
            raise ValueError("File too large (max 10MB)")
        
        # Calculate hash
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        logger.info(f"Prepared file for sending: {filename}", event="file_send")
        return filename, file_size, file_hash, file_data
    
    def verify_file_hash(self, file_data, expected_hash):
        """
        Verify file integrity using hash.
        
        Args:
            file_data: File content bytes
            expected_hash: Expected SHA256 hash
            
        Returns:
            bool: True if hash matches
        """
        actual_hash = hashlib.sha256(file_data).hexdigest()
        return actual_hash == expected_hash
