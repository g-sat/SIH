#!/usr/bin/env python3
"""
Test script for attendance API endpoints
"""

import requests
import json

def test_attendance_api():
    """Test the attendance API endpoints"""
    print('🔍 Testing Local Attendance API Endpoints')
    print('=' * 50)

    base_url = 'http://localhost:5000'

    try:
        # Test health check with new features
        print('\n1. Testing health check...')
        response = requests.get(f'{base_url}/api/health')
        if response.status_code == 200:
            data = response.json()
            print('✅ Health check passed')
            if 'features' in data and 'attendance_tracking' in data['features']:
                print('✅ Attendance tracking feature available')
            else:
                print('⚠️  Attendance tracking feature not listed')
        else:
            print(f'❌ Health check failed: {response.status_code}')
        
        # Test manual attendance recording
        print('\n2. Testing manual attendance recording...')
        attendance_data = {
            'person_name': 'Sathwik',
            'confidence': 0.95,
            'location': 'API Test Camera',
            'device_info': {'method': 'api_test', 'source': 'manual'}
        }
        
        response = requests.post(f'{base_url}/api/attendance/record', 
                               json=attendance_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            attendance_id = data.get('attendance_id')
            person_name = data.get('person_name')
            confidence = data.get('confidence')
            print(f'✅ Attendance recorded: ID {attendance_id}')
            print(f'   Person: {person_name}')
            print(f'   Confidence: {confidence:.1%}')
        else:
            print(f'❌ Failed to record attendance: {response.status_code}')
            print(f'   Response: {response.text}')
        
        # Test getting attendance summary
        print('\n3. Testing attendance summary...')
        response = requests.get(f'{base_url}/api/attendance/summary')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ Retrieved attendance summary')
            date = data.get('date')
            total_people = data.get('total_people')
            print(f'   Date: {date}')
            print(f'   Total people: {total_people}')
            
            if data.get('summary'):
                print('   People attended today:')
                for record in data['summary']:
                    name = record.get('person_name', 'Unknown')
                    detections = record.get('total_detections', 0)
                    confidence = record.get('average_confidence', 0)
                    print(f'     - {name}: {detections} detections, avg confidence: {confidence:.1%}')
            else:
                print('   No attendance records for today')
        else:
            print(f'❌ Failed to get attendance summary: {response.status_code}')
            print(f'   Response: {response.text}')
        
        # Test getting attendance records
        print('\n4. Testing attendance records...')
        response = requests.get(f'{base_url}/api/attendance/records')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ Retrieved attendance records')
            count = data.get('count')
            print(f'   Total records: {count}')
            
            if data.get('records'):
                print('   Recent records:')
                for record in data['records'][:3]:  # Show first 3
                    name = record.get('person_name', 'Unknown')
                    confidence = record.get('confidence', 0)
                    time = record.get('detection_time', 'Unknown')
                    print(f'     - {name}: {confidence:.1%} at {time}')
            else:
                print('   No attendance records found')
        else:
            print(f'❌ Failed to get attendance records: {response.status_code}')
            print(f'   Response: {response.text}')
        
        print('\n🎉 Local Attendance API testing complete!')
        
    except Exception as e:
        print(f'❌ Error during testing: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_attendance_api()
