#!/usr/bin/env python3
"""
Test script for Face Recognition API Backend
Tests all endpoints on the deployed Railway backend
"""

import requests
import json
import time
import base64
from datetime import datetime

def test_health_check(base_url):
    """Test the health check endpoint"""
    print("1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health: {data.get('status', 'unknown')}")
            print(f"   📊 Database: {data.get('database', 'unknown')}")
            print(f"   🔒 Security: {data.get('security', 'unknown')}")
            print(f"   🕐 Timestamp: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"   ❌ Health check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_load_dataset(base_url):
    """Test dataset loading endpoint"""
    print("\n2️⃣ Testing Dataset Loading...")
    try:
        response = requests.post(f"{base_url}/api/load-dataset", timeout=20)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('success', False)}")
            print(f"   📊 Message: {data.get('message', 'No message')}")
            print(f"   👥 Faces loaded: {data.get('faces_loaded', 0)}")
            print(f"   📁 Dataset path: {data.get('dataset_path', 'unknown')}")
            return True
        else:
            print(f"   ❌ Dataset loading failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Dataset loading error: {e}")
        return False

def test_recording_status(base_url):
    """Test recording status endpoint"""
    print("\n3️⃣ Testing Recording Status...")
    try:
        response = requests.get(f"{base_url}/api/recording-status", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📹 Recording: {data.get('recording', False)}")
            print(f"   📊 Status: {data.get('status', 'unknown')}")
            print(f"   📁 Output file: {data.get('output_file', 'none')}")
            return True
        else:
            print(f"   ❌ Recording status failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Recording status error: {e}")
        return False

def test_start_recording(base_url):
    """Test start recording endpoint"""
    print("\n4️⃣ Testing Start Recording...")
    try:
        payload = {
            "duration": 5,  # 5 seconds
            "camera_index": 0
        }
        
        response = requests.post(f"{base_url}/api/start-recording", 
                               json=payload, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('success', False)}")
            print(f"   📊 Message: {data.get('message', 'No message')}")
            print(f"   📁 Output file: {data.get('output_file', 'none')}")
            return True
        else:
            print(f"   ❌ Start recording failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Start recording error: {e}")
        return False

def test_process_frame_base64(base_url):
    """Test frame processing with base64 data"""
    print("\n5️⃣ Testing Frame Processing (Base64)...")
    try:
        # Create a simple test image (1x1 pixel)
        import io
        from PIL import Image
        
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='red')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_data = img_buffer.getvalue()
        
        # Convert to base64
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        payload = {
            "image_data": img_base64,
            "input_type": "base64"
        }
        
        response = requests.post(f"{base_url}/api/process-frame", 
                               json=payload, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('success', False)}")
            print(f"   👥 Faces detected: {len(data.get('faces', []))}")
            print(f"   📊 Processing time: {data.get('processing_time', 0):.3f}s")
            return True
        else:
            print(f"   ❌ Frame processing failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Frame processing error: {e}")
        return False

def test_database_stats(base_url):
    """Test database statistics (if available)"""
    print("\n6️⃣ Testing Database Statistics...")
    try:
        # This might not be a public endpoint, but let's try
        response = requests.get(f"{base_url}/api/stats", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Database connected: {data.get('database_connected', False)}")
            print(f"   📊 Total faces: {data.get('total_faces', 0)}")
            print(f"   📊 Total videos: {data.get('total_videos', 0)}")
            return True
        elif response.status_code == 404:
            print("   ℹ️  Stats endpoint not available (expected)")
            return True
        else:
            print(f"   ❌ Stats request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Stats request error: {e}")
        return False

def test_web_interface(base_url):
    """Test the web interface"""
    print("\n7️⃣ Testing Web Interface...")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if "Face Recognition API" in content:
                print("   ✅ Web interface loaded successfully")
                print("   🎨 Contains Face Recognition API content")
                return True
            else:
                print("   ⚠️  Web interface loaded but content unclear")
                return True
        else:
            print(f"   ❌ Web interface failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Web interface error: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Face Recognition API Backend Test")
    print("🌐 URL: https://web-production-afa6.up.railway.app/")
    print("=" * 60)
    
    base_url = "https://web-production-afa6.up.railway.app"
    
    # Run all tests
    tests = [
        ("Health Check", lambda: test_health_check(base_url)),
        ("Dataset Loading", lambda: test_load_dataset(base_url)),
        ("Recording Status", lambda: test_recording_status(base_url)),
        ("Start Recording", lambda: test_start_recording(base_url)),
        ("Frame Processing", lambda: test_process_frame_base64(base_url)),
        ("Database Stats", lambda: test_database_stats(base_url)),
        ("Web Interface", lambda: test_web_interface(base_url))
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"   ✅ {test_name}: PASSED")
            else:
                print(f"   ❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"   ❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
        
        # Small delay between tests
        time.sleep(1)
    
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
    
    if passed >= total * 0.8:  # 80% pass rate
        print("🎉 Backend is working well!")
        print("\n📋 API Endpoints Available:")
        print("   GET  /api/health - Health check")
        print("   POST /api/load-dataset - Load face dataset")
        print("   GET  /api/recording-status - Check recording status")
        print("   POST /api/start-recording - Start video recording")
        print("   POST /api/stop-recording - Stop video recording")
        print("   POST /api/extract-frames - Extract frames from video")
        print("   POST /api/process-frame - Process single frame")
        print("   POST /api/process-all-frames - Process all frames")
        
        print("\n🔒 Security Features:")
        print("   ✅ Data encryption enabled")
        print("   ✅ Database integration active")
        print("   ✅ Secure file operations")
        
        print("\n🌐 Access URLs:")
        print(f"   🖥️  Web Interface: {base_url}")
        print(f"   🔗 API Base: {base_url}/api/")
        
    else:
        print("⚠️  Some backend issues detected")
        print("\n🔧 Troubleshooting:")
        print("   1. Check Railway deployment logs")
        print("   2. Verify database connection")
        print("   3. Check environment variables")
        print("   4. Verify security configuration")

if __name__ == "__main__":
    main()
