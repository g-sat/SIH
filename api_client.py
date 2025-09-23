import requests
import json
import time
import base64
import cv2
import numpy as np
from pathlib import Path

class FaceRecognitionAPIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        
    def health_check(self):
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/api/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def load_dataset(self):
        """Load the face recognition dataset"""
        try:
            response = requests.post(f"{self.base_url}/api/load-dataset")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def start_recording(self, camera_index=1, duration=10):
        """Start video recording"""
        try:
            data = {
                "camera_index": camera_index,
                "duration": duration
            }
            response = requests.post(f"{self.base_url}/api/start-recording", json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def stop_recording(self):
        """Stop video recording"""
        try:
            response = requests.post(f"{self.base_url}/api/stop-recording")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_recording_status(self):
        """Get recording status"""
        try:
            response = requests.get(f"{self.base_url}/api/recording-status")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def extract_frames(self, frame_interval=5):
        """Extract frames from recorded video"""
        try:
            data = {"frame_interval": frame_interval}
            response = requests.post(f"{self.base_url}/api/extract-frames", json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def process_frame_from_file(self, image_path):
        """Process a frame from file"""
        try:
            with open(image_path, 'rb') as f:
                files = {'frame_file': f}
                response = requests.post(f"{self.base_url}/api/process-frame", files=files)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def process_frame_from_path(self, frame_path):
        """Process a frame by providing file path"""
        try:
            data = {"frame_path": frame_path}
            response = requests.post(f"{self.base_url}/api/process-frame", json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def process_frame_from_base64(self, base64_image):
        """Process a frame from base64 encoded image"""
        try:
            data = {"frame_base64": base64_image}
            response = requests.post(f"{self.base_url}/api/process-frame", json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def process_all_frames(self):
        """Process all extracted frames"""
        try:
            response = requests.post(f"{self.base_url}/api/process-all-frames")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def demo_workflow():
    """Demonstrate the complete workflow"""
    print("🚀 Face Recognition API Demo")
    print("=" * 50)
    
    client = FaceRecognitionAPIClient()
    
    # 1. Health check
    print("1. Checking API health...")
    health = client.health_check()
    print(f"   Status: {health}")
    
    if "error" in health:
        print("❌ API not available. Make sure to run: python face_recognition_api.py")
        return
    
    # 2. Load dataset
    print("\n2. Loading face recognition dataset...")
    dataset_result = client.load_dataset()
    print(f"   Result: {dataset_result}")
    
    if not dataset_result.get("success"):
        print("❌ Failed to load dataset")
        return
    
    # 3. Start recording
    print("\n3. Starting video recording...")
    recording_duration = 5  # seconds
    record_result = client.start_recording(camera_index=1, duration=recording_duration)
    print(f"   Result: {record_result}")
    
    if not record_result.get("success"):
        print("❌ Failed to start recording")
        return
    
    # 4. Monitor recording status
    print(f"\n4. Recording for {recording_duration} seconds...")
    for i in range(recording_duration + 1):
        status = client.get_recording_status()
        print(f"   Status: Recording={status.get('is_recording')}, Frames={status.get('frames_captured')}")
        time.sleep(1)
    
    # 5. Extract frames
    print("\n5. Extracting frames from video...")
    frames_result = client.extract_frames(frame_interval=10)  # Every 10th frame
    print(f"   Result: {frames_result}")
    
    if not frames_result.get("success"):
        print("❌ Failed to extract frames")
        return
    
    # 6. Process all frames
    print("\n6. Processing all frames for face recognition...")
    process_result = client.process_all_frames()
    print(f"   Result: {process_result}")
    
    if process_result.get("success"):
        print(f"✅ Successfully processed {len(process_result.get('results', []))} frames")
        print(f"   Total faces detected: {process_result.get('total_faces_detected', 0)}")
        
        # Show detection details
        for result in process_result.get('results', []):
            if result['faces_found'] > 0:
                print(f"   📸 {result['frame_file']}: {result['faces_found']} faces")
                for detection in result['detections']:
                    print(f"      - {detection['name']} ({detection['confidence']}%)")

def test_single_image():
    """Test processing a single image"""
    print("\n🖼️  Testing single image processing...")
    
    client = FaceRecognitionAPIClient()
    
    # Test with an image from dataset
    dataset_path = Path("./dataset")
    image_files = list(dataset_path.glob("*.png")) + list(dataset_path.glob("*.jpg"))
    
    if image_files:
        test_image = image_files[0]
        print(f"Testing with: {test_image}")
        
        result = client.process_frame_from_file(str(test_image))
        print(f"Result: {result}")
        
        if result.get("success"):
            print(f"✅ Detected {result.get('faces_found', 0)} faces")
            for detection in result.get('detections', []):
                print(f"   - {detection['name']} ({detection['confidence']}%)")
    else:
        print("❌ No test images found in dataset")

if __name__ == "__main__":
    print("Face Recognition API Client")
    print("Choose an option:")
    print("1. Run complete demo workflow")
    print("2. Test single image processing")
    print("3. Health check only")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        demo_workflow()
    elif choice == "2":
        client = FaceRecognitionAPIClient()
        
        # Load dataset first
        print("Loading dataset...")
        dataset_result = client.load_dataset()
        print(f"Dataset result: {dataset_result}")
        
        if dataset_result.get("success"):
            test_single_image()
        else:
            print("❌ Failed to load dataset")
    elif choice == "3":
        client = FaceRecognitionAPIClient()
        health = client.health_check()
        print(f"Health check: {health}")
    else:
        print("Invalid choice")
