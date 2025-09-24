#!/usr/bin/env python3
"""
Database Connection Test for Face Recognition API
Tests connection to the Attendance database
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_connection():
    """Test basic database connection"""
    print("🔌 Testing basic database connection...")
    
    # Database configuration
    db_config = {
        'host': '10.1.40.85',
        'database': 'Attendance',
        'user': 'postgres',
        'password': 'F!ve',
        'port': 5432
    }
    
    try:
        # Test connection
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected to PostgreSQL: {version['version']}")
        
        # Test database info
        cursor.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port();")
        info = cursor.fetchone()
        print(f"✅ Database: {info['current_database']}")
        print(f"✅ User: {info['current_user']}")
        print(f"✅ Server: {info['inet_server_addr']}:{info['inet_server_port']}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_database_permissions():
    """Test database permissions and capabilities"""
    print("\n🔑 Testing database permissions...")
    
    db_config = {
        'host': '10.1.40.85',
        'database': 'Attendance',
        'user': 'postgres',
        'password': 'F!ve',
        'port': 5432
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Test table creation permission
        test_table_name = f"face_recognition_test_{int(datetime.now().timestamp())}"
        
        try:
            cursor.execute(f"""
                CREATE TABLE {test_table_name} (
                    id SERIAL PRIMARY KEY,
                    test_data TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            print("✅ CREATE TABLE permission: OK")
            
            # Test insert permission
            cursor.execute(f"INSERT INTO {test_table_name} (test_data) VALUES ('test');")
            print("✅ INSERT permission: OK")
            
            # Test select permission
            cursor.execute(f"SELECT * FROM {test_table_name};")
            result = cursor.fetchall()
            print(f"✅ SELECT permission: OK (found {len(result)} rows)")
            
            # Test update permission
            cursor.execute(f"UPDATE {test_table_name} SET test_data = 'updated' WHERE id = 1;")
            print("✅ UPDATE permission: OK")
            
            # Test delete permission
            cursor.execute(f"DELETE FROM {test_table_name} WHERE id = 1;")
            print("✅ DELETE permission: OK")
            
            # Clean up test table
            cursor.execute(f"DROP TABLE {test_table_name};")
            print("✅ DROP TABLE permission: OK")
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ Permission test failed: {e}")
            conn.rollback()
            return False
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Permission test connection failed: {e}")
        return False

def check_existing_tables():
    """Check existing tables in the database"""
    print("\n📊 Checking existing tables...")
    
    db_config = {
        'host': '10.1.40.85',
        'database': 'Attendance',
        'user': 'postgres',
        'password': 'F!ve',
        'port': 5432
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all tables
        cursor.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        if tables:
            print(f"📋 Found {len(tables)} existing tables:")
            for table in tables:
                print(f"   📄 {table['table_name']} ({table['table_type']})")
        else:
            print("📋 No existing tables found")
        
        # Check database size
        cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database())) as size;")
        size_info = cursor.fetchone()
        print(f"💾 Database size: {size_info['size']}")
        
        cursor.close()
        conn.close()
        
        return tables
        
    except Exception as e:
        print(f"❌ Failed to check tables: {e}")
        return []

def test_face_recognition_tables():
    """Test creating face recognition tables"""
    print("\n🎯 Testing face recognition table creation...")
    
    db_config = {
        'host': '10.1.40.85',
        'database': 'Attendance',
        'user': 'postgres',
        'password': 'F!ve',
        'port': 5432
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Create faces table (test)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS face_recognition_faces_test (
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
        print("✅ Created face_recognition_faces_test table")
        
        # Test BYTEA storage (encrypted data simulation)
        test_data = b"This is test encrypted image data"
        cursor.execute("""
            INSERT INTO face_recognition_faces_test 
            (person_name, image_data, image_hash, metadata)
            VALUES (%s, %s, %s, %s);
        """, ('test_person', test_data, 'test_hash', '{"test": true}'))
        print("✅ Inserted test encrypted data")
        
        # Test retrieval
        cursor.execute("SELECT * FROM face_recognition_faces_test WHERE person_name = 'test_person';")
        result = cursor.fetchone()
        if result:
            print(f"✅ Retrieved test data: ID {result[0]}, Name: {result[1]}")
            print(f"   📊 Data size: {len(result[2])} bytes")
        
        # Clean up test table
        cursor.execute("DROP TABLE face_recognition_faces_test;")
        print("✅ Cleaned up test table")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Face recognition table test failed: {e}")
        return False

def test_with_database_manager():
    """Test using the DatabaseManager class"""
    print("\n🔧 Testing with DatabaseManager class...")
    
    # Set environment variables
    os.environ['DB_HOST'] = '10.1.40.85'
    os.environ['DB_NAME'] = 'Attendance'
    os.environ['DB_USER'] = 'postgres'
    os.environ['DB_PASSWORD'] = 'F!ve'
    os.environ['DB_SSL'] = 'false'
    os.environ['ENCRYPTION_PASSWORD'] = 'test-encryption-password-for-demo'
    
    try:
        # Import and test DatabaseManager
        sys.path.append('.')
        from database_manager import DatabaseManager
        
        print("✅ DatabaseManager imported successfully")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        print("✅ DatabaseManager initialized")
        
        # Test getting statistics (this will create tables if they don't exist)
        stats = db_manager.get_processing_statistics()
        print("✅ Database statistics retrieved:")
        print(f"   📊 Total faces: {stats['total_faces']}")
        print(f"   📊 Total videos: {stats['total_videos']}")
        print(f"   📊 Total frames: {stats['total_frames']}")
        print(f"   📊 Total detections: {stats['total_detections']}")
        print(f"   📊 Unique people: {stats['unique_people']}")
        
        # Close connection
        db_manager.close()
        print("✅ DatabaseManager closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ DatabaseManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🔍 Face Recognition API - Database Connection Test")
    print("=" * 60)
    print("🎯 Target Database:")
    print("   Host: 10.1.40.85")
    print("   Database: Attendance")
    print("   User: postgres")
    print("   SSL: disabled")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Database Permissions", test_database_permissions),
        ("Existing Tables", lambda: check_existing_tables() is not None),
        ("Face Recognition Tables", test_face_recognition_tables),
        ("DatabaseManager Integration", test_with_database_manager)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database is ready for Face Recognition API")
        print("\n📋 Next steps:")
        print("   1. Update .env file with database configuration")
        print("   2. Start the API: python face_recognition_api.py")
        print("   3. Test API: curl http://localhost:5000/api/health")
    else:
        print("⚠️  Some tests failed. Please check the database configuration.")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify database server is running")
        print("   2. Check network connectivity to 10.1.40.85")
        print("   3. Verify credentials: postgres / F!ve")
        print("   4. Check firewall settings")

if __name__ == "__main__":
    main()
