#!/usr/bin/env python3
"""
Security Setup Script for Face Recognition API
Sets up PostgreSQL database and encryption
"""

import os
import sys
import subprocess
import secrets
import string
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def generate_secure_password(length=32):
    """Generate a cryptographically secure password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def create_env_file():
    """Create .env file with secure configuration"""
    print("🔐 Creating secure environment configuration...")
    
    # Generate secure passwords
    encryption_password = generate_secure_password(64)
    api_key = generate_secure_password(32)
    db_password = generate_secure_password(16)
    
    env_content = f"""# Face Recognition API - Secure Configuration
# Generated on {os.popen('date').read().strip()}

# Database Configuration
DATABASE_URL=postgresql://face_recognition_user:{db_password}@localhost:5432/face_recognition_db

# Security Configuration (KEEP SECRET!)
ENCRYPTION_PASSWORD={encryption_password}

# API Security
API_KEY={api_key}
ALLOWED_ORIGINS=https://yourdomain.com,http://localhost:3000

# Flask Configuration
FLASK_ENV=production
PORT=5000
DEBUG=False

# File Upload Limits
MAX_UPLOAD_SIZE=10485760
MAX_VIDEO_DURATION=300

# Database Connection Pool
DB_MIN_CONNECTIONS=2
DB_MAX_CONNECTIONS=20

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/face_recognition_api.log

# Cleanup Configuration
AUTO_CLEANUP_DAYS=30
CLEANUP_SCHEDULE=daily

# Performance Configuration
FACE_DETECTION_SCALE_FACTOR=1.1
FACE_DETECTION_MIN_NEIGHBORS=3
FACE_DETECTION_MIN_SIZE=30
FACE_DETECTION_MAX_SIZE=300

# Security Features
SECURE_FILE_DELETION=true
INTEGRITY_CHECKING=true
AUDIT_LOGGING=true
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with secure configuration")
    print("⚠️  IMPORTANT: Keep the .env file secure and never commit it to version control!")
    
    return {
        'db_password': db_password,
        'encryption_password': encryption_password,
        'api_key': api_key
    }

def setup_postgresql():
    """Set up PostgreSQL database and user"""
    print("🐘 Setting up PostgreSQL database...")
    
    try:
        # Check if PostgreSQL is installed
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ PostgreSQL is not installed or not in PATH")
            print("📥 Please install PostgreSQL first:")
            print("   - Windows: https://www.postgresql.org/download/windows/")
            print("   - macOS: brew install postgresql")
            print("   - Ubuntu: sudo apt-get install postgresql postgresql-contrib")
            return False
        
        print(f"✅ Found PostgreSQL: {result.stdout.strip()}")
        
        # Get database credentials from user
        print("\n🔑 Database Setup:")
        print("Please provide PostgreSQL superuser credentials to create the database and user.")
        
        pg_host = input("PostgreSQL host (default: localhost): ").strip() or "localhost"
        pg_port = input("PostgreSQL port (default: 5432): ").strip() or "5432"
        pg_superuser = input("PostgreSQL superuser (default: postgres): ").strip() or "postgres"
        pg_superuser_password = input("PostgreSQL superuser password: ").strip()
        
        if not pg_superuser_password:
            print("❌ Superuser password is required")
            return False
        
        # Connect to PostgreSQL as superuser
        conn = psycopg2.connect(
            host=pg_host,
            port=pg_port,
            user=pg_superuser,
            password=pg_superuser_password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Generate secure password for application user
        app_user_password = generate_secure_password(16)
        
        # Create database and user
        print("📊 Creating database and user...")
        
        try:
            cursor.execute("CREATE DATABASE face_recognition_db;")
            print("✅ Created database: face_recognition_db")
        except psycopg2.errors.DuplicateDatabase:
            print("ℹ️  Database face_recognition_db already exists")
        
        try:
            cursor.execute("CREATE USER face_recognition_user WITH PASSWORD %s;", (app_user_password,))
            print("✅ Created user: face_recognition_user")
        except psycopg2.errors.DuplicateObject:
            print("ℹ️  User face_recognition_user already exists")
            cursor.execute("ALTER USER face_recognition_user WITH PASSWORD %s;", (app_user_password,))
            print("✅ Updated password for face_recognition_user")
        
        # Grant permissions
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE face_recognition_db TO face_recognition_user;")
        cursor.execute("ALTER USER face_recognition_user CREATEDB;")
        print("✅ Granted permissions to face_recognition_user")
        
        cursor.close()
        conn.close()
        
        print("🎉 PostgreSQL setup completed successfully!")
        return app_user_password
        
    except Exception as e:
        print(f"❌ PostgreSQL setup failed: {e}")
        print("\n🔧 Manual setup instructions:")
        print("1. Install PostgreSQL")
        print("2. Create database: CREATE DATABASE face_recognition_db;")
        print("3. Create user: CREATE USER face_recognition_user WITH PASSWORD 'your_password';")
        print("4. Grant permissions: GRANT ALL PRIVILEGES ON DATABASE face_recognition_db TO face_recognition_user;")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing security dependencies...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directory structure...")
    
    directories = [
        'logs',
        'backups',
        'temp',
        'extracted_frames'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_security_setup():
    """Test the security setup"""
    print("🧪 Testing security setup...")
    
    try:
        from security_manager import SecurityManager
        from database_manager import DatabaseManager
        
        # Test encryption
        security = SecurityManager()
        test_data = b"Test encryption data"
        encrypted = security.encrypt_image(test_data)
        decrypted = security.decrypt_image(encrypted)
        
        if test_data == decrypted:
            print("✅ Encryption/decryption test passed")
        else:
            print("❌ Encryption/decryption test failed")
            return False
        
        # Test database connection
        try:
            database = DatabaseManager()
            stats = database.get_processing_statistics()
            print("✅ Database connection test passed")
            database.close()
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
            return False
        
        print("🎉 All security tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Security modules not available: {e}")
        return False

def main():
    """Main setup function"""
    print("🔒 Face Recognition API - Security Setup")
    print("=" * 50)
    
    # Check if already configured
    if Path('.env').exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Setup cancelled")
            return
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed: Could not install dependencies")
        return
    
    # Create directories
    create_directories()
    
    # Set up PostgreSQL
    db_password = setup_postgresql()
    if not db_password:
        print("❌ Setup failed: Could not set up PostgreSQL")
        return
    
    # Create environment file
    credentials = create_env_file()
    
    # Update .env with actual database password
    if db_password:
        with open('.env', 'r') as f:
            content = f.read()
        
        content = content.replace(
            f"postgresql://face_recognition_user:{credentials['db_password']}@localhost:5432/face_recognition_db",
            f"postgresql://face_recognition_user:{db_password}@localhost:5432/face_recognition_db"
        )
        
        with open('.env', 'w') as f:
            f.write(content)
    
    # Test setup
    if test_security_setup():
        print("\n🎉 Security setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Review the .env file and adjust settings as needed")
        print("2. Start the API server: python face_recognition_api.py")
        print("3. Test the API: curl http://localhost:5000/api/health")
        print("\n🔐 Security notes:")
        print("- Keep the .env file secure and never commit it to version control")
        print("- Regularly rotate the encryption password")
        print("- Monitor database access logs")
        print("- Set up regular backups of encrypted data")
    else:
        print("❌ Setup completed with errors. Please check the configuration.")

if __name__ == "__main__":
    main()
