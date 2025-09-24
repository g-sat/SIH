#!/usr/bin/env python3
"""
Database Manager for Face Recognition API
Handles PostgreSQL operations for secure data storage
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import base64
from security_manager import SecurityManager

class DatabaseManager:
    def __init__(self, database_url=None, encryption_password=None):
        """
        Initialize database manager with PostgreSQL connection

        Args:
            database_url (str): PostgreSQL connection URL
            encryption_password (str): Password for encryption
        """
        self.logger = logging.getLogger(__name__)

        # Initialize security manager
        self.security = SecurityManager(encryption_password)

        # Database connection parameters - support both URL and individual components
        if database_url:
            self.database_url = database_url
        else:
            # Build connection URL from environment variables
            db_host = os.environ.get('DB_HOST', 'localhost')
            db_name = os.environ.get('DB_NAME', 'face_recognition')
            db_user = os.environ.get('DB_USER', 'postgres')
            db_password = os.environ.get('DB_PASSWORD', '')
            db_port = os.environ.get('DB_PORT', '5432')
            db_ssl = os.environ.get('DB_SSL', 'false').lower()

            # Build connection string
            ssl_mode = 'require' if db_ssl == 'true' else 'disable'
            self.database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode={ssl_mode}"

        self.logger.info(f"Database URL configured: {self.database_url.split('@')[0]}@***")
        
        # Connection pool
        self.pool = None
        self._initialize_connection_pool()
        self._create_tables()
        
        self.logger.info("Database manager initialized with encryption")
    
    def _initialize_connection_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=self.database_url
            )
            self.logger.info("Database connection pool created")
        except Exception as e:
            self.logger.error(f"Failed to create connection pool: {e}")
            raise
    
    def _get_connection(self):
        """Get connection from pool"""
        return self.pool.getconn()
    
    def _put_connection(self, conn):
        """Return connection to pool"""
        self.pool.putconn(conn)
    
    def _create_tables(self):
        """Create necessary database tables"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create faces table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS faces (
                    id SERIAL PRIMARY KEY,
                    person_name VARCHAR(255) NOT NULL,
                    image_data BYTEA NOT NULL,
                    image_hash VARCHAR(64) NOT NULL,
                    face_encoding BYTEA,
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Create videos table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    video_data BYTEA NOT NULL,
                    video_hash VARCHAR(64) NOT NULL,
                    duration FLOAT,
                    fps INTEGER,
                    resolution VARCHAR(50),
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Create frames table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS frames (
                    id SERIAL PRIMARY KEY,
                    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
                    frame_number INTEGER NOT NULL,
                    frame_data BYTEA NOT NULL,
                    frame_hash VARCHAR(64) NOT NULL,
                    timestamp_ms FLOAT,
                    faces_detected INTEGER DEFAULT 0,
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Create face_detections table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS face_detections (
                    id SERIAL PRIMARY KEY,
                    frame_id INTEGER REFERENCES frames(id) ON DELETE CASCADE,
                    face_id INTEGER REFERENCES faces(id),
                    person_name VARCHAR(255),
                    confidence FLOAT NOT NULL,
                    bounding_box JSONB NOT NULL,
                    face_encoding BYTEA,
                    is_verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Create processing_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_sessions (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    total_frames INTEGER DEFAULT 0,
                    processed_frames INTEGER DEFAULT 0,
                    faces_detected INTEGER DEFAULT 0,
                    metadata JSONB,
                    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    completed_at TIMESTAMP WITH TIME ZONE
                );
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_faces_person_name ON faces(person_name);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_faces_created_at ON faces(created_at);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_filename ON videos(filename);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_frames_video_id ON frames(video_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_face_detections_frame_id ON face_detections(frame_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_face_detections_confidence ON face_detections(confidence);")
            
            conn.commit()
            self.logger.info("Database tables created/verified successfully")
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Failed to create tables: {e}")
            raise
        finally:
            if conn:
                self._put_connection(conn)
    
    def store_face_image(self, person_name: str, image_data: bytes, face_encoding: bytes = None, metadata: dict = None) -> int:
        """
        Store encrypted face image in database
        
        Args:
            person_name (str): Name of the person
            image_data (bytes): Raw image data
            face_encoding (bytes): Face encoding data
            metadata (dict): Additional metadata
            
        Returns:
            int: Face ID
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Encrypt image data
            encrypted_image = self.security.encrypt_image(image_data)
            
            # Generate hash for integrity
            image_hash = self.security.generate_file_hash_from_bytes(image_data)
            
            # Encrypt face encoding if provided
            encrypted_encoding = None
            if face_encoding:
                encrypted_encoding = self.security.encrypt_image(face_encoding)
            
            # Insert face record
            cursor.execute("""
                INSERT INTO faces (person_name, image_data, image_hash, face_encoding, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (person_name, encrypted_image, image_hash, encrypted_encoding, json.dumps(metadata or {})))
            
            face_id = cursor.fetchone()[0]
            conn.commit()
            
            self.logger.info(f"Stored encrypted face image for {person_name} with ID {face_id}")
            return face_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Failed to store face image: {e}")
            raise
        finally:
            if conn:
                self._put_connection(conn)
    
    def get_face_image(self, face_id: int) -> Tuple[str, bytes, bytes]:
        """
        Retrieve and decrypt face image from database
        
        Args:
            face_id (int): Face ID
            
        Returns:
            Tuple[str, bytes, bytes]: (person_name, image_data, face_encoding)
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT person_name, image_data, face_encoding
                FROM faces WHERE id = %s;
            """, (face_id,))
            
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Face with ID {face_id} not found")
            
            # Decrypt image data
            decrypted_image = self.security.decrypt_image(result['image_data'])
            
            # Decrypt face encoding if available
            decrypted_encoding = None
            if result['face_encoding']:
                decrypted_encoding = self.security.decrypt_image(result['face_encoding'])
            
            return result['person_name'], decrypted_image, decrypted_encoding
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve face image: {e}")
            raise
        finally:
            if conn:
                self._put_connection(conn)
    
    def get_all_faces(self) -> List[Dict]:
        """
        Get all faces from database (decrypted)
        
        Returns:
            List[Dict]: List of face records
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT id, person_name, image_hash, metadata, created_at
                FROM faces ORDER BY person_name, created_at;
            """)
            
            faces = []
            for row in cursor.fetchall():
                # Get decrypted image data
                person_name, image_data, face_encoding = self.get_face_image(row['id'])
                
                faces.append({
                    'id': row['id'],
                    'person_name': person_name,
                    'image_data': image_data,
                    'face_encoding': face_encoding,
                    'image_hash': row['image_hash'],
                    'metadata': row['metadata'],
                    'created_at': row['created_at']
                })
            
            self.logger.info(f"Retrieved {len(faces)} faces from database")
            return faces
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve faces: {e}")
            raise
        finally:
            if conn:
                self._put_connection(conn)
    
    def store_video(self, filename: str, video_data: bytes, duration: float = None, fps: int = None, resolution: str = None, metadata: dict = None) -> int:
        """
        Store encrypted video in database
        
        Args:
            filename (str): Video filename
            video_data (bytes): Raw video data
            duration (float): Video duration in seconds
            fps (int): Frames per second
            resolution (str): Video resolution (e.g., "1920x1080")
            metadata (dict): Additional metadata
            
        Returns:
            int: Video ID
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Encrypt video data
            encrypted_video = self.security.encrypt_image(video_data)
            
            # Generate hash for integrity
            video_hash = self.security.generate_file_hash_from_bytes(video_data)
            
            # Insert video record
            cursor.execute("""
                INSERT INTO videos (filename, video_data, video_hash, duration, fps, resolution, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (filename, encrypted_video, video_hash, duration, fps, resolution, json.dumps(metadata or {})))
            
            video_id = cursor.fetchone()[0]
            conn.commit()
            
            self.logger.info(f"Stored encrypted video {filename} with ID {video_id}")
            return video_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Failed to store video: {e}")
            raise
        finally:
            if conn:
                self._put_connection(conn)
    
    def store_frame(self, video_id: int, frame_number: int, frame_data: bytes, timestamp_ms: float = None, metadata: dict = None) -> int:
        """
        Store encrypted video frame in database
        
        Args:
            video_id (int): Video ID
            frame_number (int): Frame number
            frame_data (bytes): Raw frame data
            timestamp_ms (float): Frame timestamp in milliseconds
            metadata (dict): Additional metadata
            
        Returns:
            int: Frame ID
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Encrypt frame data
            encrypted_frame = self.security.encrypt_image(frame_data)
            
            # Generate hash for integrity
            frame_hash = self.security.generate_file_hash_from_bytes(frame_data)
            
            # Insert frame record
            cursor.execute("""
                INSERT INTO frames (video_id, frame_number, frame_data, frame_hash, timestamp_ms, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (video_id, frame_number, encrypted_frame, frame_hash, timestamp_ms, json.dumps(metadata or {})))
            
            frame_id = cursor.fetchone()[0]
            conn.commit()
            
            self.logger.debug(f"Stored encrypted frame {frame_number} for video {video_id}")
            return frame_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Failed to store frame: {e}")
            raise
        finally:
            if conn:
                self._put_connection(conn)
    
    def store_face_detection(self, frame_id: int, person_name: str, confidence: float, bounding_box: dict, face_id: int = None, face_encoding: bytes = None) -> int:
        """
        Store face detection result
        
        Args:
            frame_id (int): Frame ID
            person_name (str): Detected person name
            confidence (float): Detection confidence
            bounding_box (dict): Face bounding box coordinates
            face_id (int): Reference to known face (optional)
            face_encoding (bytes): Face encoding data (optional)
            
        Returns:
            int: Detection ID
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Encrypt face encoding if provided
            encrypted_encoding = None
            if face_encoding:
                encrypted_encoding = self.security.encrypt_image(face_encoding)
            
            # Insert detection record
            cursor.execute("""
                INSERT INTO face_detections (frame_id, face_id, person_name, confidence, bounding_box, face_encoding)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (frame_id, face_id, person_name, confidence, json.dumps(bounding_box), encrypted_encoding))
            
            detection_id = cursor.fetchone()[0]
            
            # Update frame faces count
            cursor.execute("""
                UPDATE frames SET faces_detected = faces_detected + 1
                WHERE id = %s;
            """, (frame_id,))
            
            conn.commit()
            
            self.logger.debug(f"Stored face detection for {person_name} in frame {frame_id}")
            return detection_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Failed to store face detection: {e}")
            raise
        finally:
            if conn:
                self._put_connection(conn)
    
    def get_processing_statistics(self) -> Dict:
        """
        Get processing statistics from database
        
        Returns:
            Dict: Statistics summary
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get counts
            cursor.execute("SELECT COUNT(*) as total_faces FROM faces;")
            total_faces = cursor.fetchone()['total_faces']
            
            cursor.execute("SELECT COUNT(*) as total_videos FROM videos;")
            total_videos = cursor.fetchone()['total_videos']
            
            cursor.execute("SELECT COUNT(*) as total_frames FROM frames;")
            total_frames = cursor.fetchone()['total_frames']
            
            cursor.execute("SELECT COUNT(*) as total_detections FROM face_detections;")
            total_detections = cursor.fetchone()['total_detections']
            
            cursor.execute("SELECT COUNT(DISTINCT person_name) as unique_people FROM faces;")
            unique_people = cursor.fetchone()['unique_people']
            
            # Get average confidence
            cursor.execute("SELECT AVG(confidence) as avg_confidence FROM face_detections;")
            avg_confidence = cursor.fetchone()['avg_confidence'] or 0
            
            stats = {
                'total_faces': total_faces,
                'total_videos': total_videos,
                'total_frames': total_frames,
                'total_detections': total_detections,
                'unique_people': unique_people,
                'average_confidence': float(avg_confidence),
                'database_size_mb': self._get_database_size()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            raise
        finally:
            if conn:
                self._put_connection(conn)
    
    def _get_database_size(self) -> float:
        """Get approximate database size in MB"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT pg_size_pretty(pg_total_relation_size('faces')) as faces_size,
                       pg_size_pretty(pg_total_relation_size('videos')) as videos_size,
                       pg_size_pretty(pg_total_relation_size('frames')) as frames_size,
                       pg_size_pretty(pg_total_relation_size('face_detections')) as detections_size;
            """)
            
            # This is a simplified calculation
            return 0.0  # Would need more complex query for exact size
            
        except Exception as e:
            self.logger.debug(f"Could not get database size: {e}")
            return 0.0
        finally:
            if conn:
                self._put_connection(conn)
    
    def cleanup_old_data(self, days_old: int = 30) -> int:
        """
        Clean up old data from database
        
        Args:
            days_old (int): Delete data older than this many days
            
        Returns:
            int: Number of records deleted
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete old processing sessions
            cursor.execute("""
                DELETE FROM processing_sessions 
                WHERE started_at < NOW() - INTERVAL '%s days';
            """, (days_old,))
            
            deleted_sessions = cursor.rowcount
            
            # Delete old videos (and cascading frames/detections)
            cursor.execute("""
                DELETE FROM videos 
                WHERE created_at < NOW() - INTERVAL '%s days';
            """, (days_old,))
            
            deleted_videos = cursor.rowcount
            
            conn.commit()
            
            total_deleted = deleted_sessions + deleted_videos
            self.logger.info(f"Cleaned up {total_deleted} old records")
            return total_deleted
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Failed to cleanup old data: {e}")
            raise
        finally:
            if conn:
                self._put_connection(conn)
    
    def close(self):
        """Close database connection pool"""
        if self.pool:
            self.pool.closeall()
            self.logger.info("Database connection pool closed")

# Add missing method to SecurityManager
def generate_file_hash_from_bytes(self, data: bytes) -> str:
    """Generate SHA256 hash from bytes"""
    import hashlib
    return hashlib.sha256(data).hexdigest()

# Monkey patch the method
SecurityManager.generate_file_hash_from_bytes = generate_file_hash_from_bytes
