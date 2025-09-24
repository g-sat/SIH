#!/usr/bin/env python3
"""
Security Manager for Face Recognition API
Handles encryption/decryption of images and videos
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import logging

class SecurityManager:
    def __init__(self, password=None):
        """
        Initialize security manager with encryption capabilities
        
        Args:
            password (str): Master password for encryption (uses env var if None)
        """
        self.logger = logging.getLogger(__name__)
        
        # Get encryption password from environment or parameter
        self.password = password or os.environ.get('ENCRYPTION_PASSWORD', 'default-face-recognition-key')
        
        # Generate encryption key from password
        self.key = self._generate_key_from_password(self.password)
        self.cipher = Fernet(self.key)
        
        self.logger.info("Security manager initialized with encryption enabled")
    
    def _generate_key_from_password(self, password: str) -> bytes:
        """Generate a Fernet key from password using PBKDF2"""
        password_bytes = password.encode()
        salt = b'face_recognition_salt_2024'  # In production, use random salt per user
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt_image(self, image_data: bytes) -> bytes:
        """
        Encrypt image data
        
        Args:
            image_data (bytes): Raw image bytes
            
        Returns:
            bytes: Encrypted image data
        """
        try:
            encrypted_data = self.cipher.encrypt(image_data)
            self.logger.debug(f"Image encrypted: {len(image_data)} -> {len(encrypted_data)} bytes")
            return encrypted_data
        except Exception as e:
            self.logger.error(f"Image encryption failed: {e}")
            raise
    
    def decrypt_image(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt image data
        
        Args:
            encrypted_data (bytes): Encrypted image bytes
            
        Returns:
            bytes: Decrypted image data
        """
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            self.logger.debug(f"Image decrypted: {len(encrypted_data)} -> {len(decrypted_data)} bytes")
            return decrypted_data
        except Exception as e:
            self.logger.error(f"Image decryption failed: {e}")
            raise
    
    def encrypt_video_frame(self, frame: np.ndarray) -> bytes:
        """
        Encrypt a video frame (numpy array)
        
        Args:
            frame (np.ndarray): OpenCV frame
            
        Returns:
            bytes: Encrypted frame data
        """
        try:
            # Convert frame to bytes
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # Encrypt the frame bytes
            encrypted_frame = self.encrypt_image(frame_bytes)
            return encrypted_frame
        except Exception as e:
            self.logger.error(f"Video frame encryption failed: {e}")
            raise
    
    def decrypt_video_frame(self, encrypted_data: bytes) -> np.ndarray:
        """
        Decrypt video frame data back to numpy array
        
        Args:
            encrypted_data (bytes): Encrypted frame data
            
        Returns:
            np.ndarray: OpenCV frame
        """
        try:
            # Decrypt the frame bytes
            frame_bytes = self.decrypt_image(encrypted_data)
            
            # Convert bytes back to numpy array
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            self.logger.error(f"Video frame decryption failed: {e}")
            raise
    
    def encrypt_file(self, file_path: str, output_path: str = None) -> str:
        """
        Encrypt a file and save to disk
        
        Args:
            file_path (str): Path to file to encrypt
            output_path (str): Output path (optional, defaults to .enc extension)
            
        Returns:
            str: Path to encrypted file
        """
        try:
            if not output_path:
                output_path = file_path + '.enc'
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = self.encrypt_image(file_data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            self.logger.info(f"File encrypted: {file_path} -> {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"File encryption failed: {e}")
            raise
    
    def decrypt_file(self, encrypted_path: str, output_path: str = None) -> str:
        """
        Decrypt a file and save to disk
        
        Args:
            encrypted_path (str): Path to encrypted file
            output_path (str): Output path (optional, removes .enc extension)
            
        Returns:
            str: Path to decrypted file
        """
        try:
            if not output_path:
                output_path = encrypted_path.replace('.enc', '')
            
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.decrypt_image(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            self.logger.info(f"File decrypted: {encrypted_path} -> {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"File decryption failed: {e}")
            raise
    
    def generate_file_hash(self, file_path: str) -> str:
        """
        Generate SHA256 hash of a file for integrity checking
        
        Args:
            file_path (str): Path to file
            
        Returns:
            str: SHA256 hash
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            file_hash = sha256_hash.hexdigest()
            self.logger.debug(f"Generated hash for {file_path}: {file_hash[:16]}...")
            return file_hash
        except Exception as e:
            self.logger.error(f"Hash generation failed: {e}")
            raise
    
    def secure_delete_file(self, file_path: str) -> bool:
        """
        Securely delete a file by overwriting with random data
        
        Args:
            file_path (str): Path to file to delete
            
        Returns:
            bool: Success status
        """
        try:
            if not os.path.exists(file_path):
                return True
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Overwrite with random data 3 times
            with open(file_path, 'r+b') as f:
                for _ in range(3):
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Finally delete the file
            os.remove(file_path)
            self.logger.info(f"Securely deleted file: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Secure file deletion failed: {e}")
            return False
    
    def encrypt_base64_image(self, base64_data: str) -> str:
        """
        Encrypt base64 encoded image data
        
        Args:
            base64_data (str): Base64 encoded image
            
        Returns:
            str: Encrypted base64 data
        """
        try:
            # Decode base64 to bytes
            image_bytes = base64.b64decode(base64_data)
            
            # Encrypt the bytes
            encrypted_bytes = self.encrypt_image(image_bytes)
            
            # Encode back to base64
            encrypted_base64 = base64.b64encode(encrypted_bytes).decode('utf-8')
            return encrypted_base64
        except Exception as e:
            self.logger.error(f"Base64 image encryption failed: {e}")
            raise
    
    def decrypt_base64_image(self, encrypted_base64: str) -> str:
        """
        Decrypt base64 encoded image data
        
        Args:
            encrypted_base64 (str): Encrypted base64 data
            
        Returns:
            str: Decrypted base64 image data
        """
        try:
            # Decode base64 to bytes
            encrypted_bytes = base64.b64decode(encrypted_base64)
            
            # Decrypt the bytes
            image_bytes = self.decrypt_image(encrypted_bytes)
            
            # Encode back to base64
            base64_data = base64.b64encode(image_bytes).decode('utf-8')
            return base64_data
        except Exception as e:
            self.logger.error(f"Base64 image decryption failed: {e}")
            raise

# Example usage and testing
if __name__ == "__main__":
    # Test the security manager
    security = SecurityManager("test-password-123")
    
    # Test with sample data
    test_data = b"This is test image data"
    
    print("🔒 Testing Security Manager...")
    
    # Test encryption/decryption
    encrypted = security.encrypt_image(test_data)
    decrypted = security.decrypt_image(encrypted)
    
    print(f"✅ Original: {len(test_data)} bytes")
    print(f"🔐 Encrypted: {len(encrypted)} bytes")
    print(f"🔓 Decrypted: {len(decrypted)} bytes")
    print(f"✅ Match: {test_data == decrypted}")
    
    print("🎉 Security Manager test completed!")
