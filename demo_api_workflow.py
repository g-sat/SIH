#!/usr/bin/env python3
"""
Demo script showing the complete Face Recognition API workflow:
1. Video Capturing API
2. Video to Frames API  
3. Face Recognition API
"""

import requests
import json
import time
import os
from pathlib import Path

class FaceRecognitionDemo:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        
    def print_step(self, step_num, title):
        print(f"\n{'='*60}")
        print(f"STEP {step_num}: {title}")
        print(f"{'='*60}")
    
    def print_result(self, result):
        print(f"✅ Result: {json.dumps(result, indent=2)}")
    
    def health_check(self):
        """Check API health"""
        self.print_step(1, "API Health Check")
        
        try:
            response = requests.get(f"{self.base_url}/api/health")
            result = response.json()
            self.print_result(result)
            
            if result.get("status") == "healthy":
                print("✅ API is healthy and ready!")
                return True
            else:
                print("❌ API is not healthy")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to API: {e}")
            print("Make sure the API server is running: python face_recognition_api.py")
            return False
    
    def load_dataset(self):
        """Load face recognition dataset"""
        self.print_step(2, "Load Face Recognition Dataset")
        
        try:
            response = requests.post(f"{self.base_url}/api/load-dataset")
            result = response.json()
            self.print_result(result)
            
            if result.get("success"):
                print(f"✅ Successfully loaded {result.get('faces_loaded')} faces from {result.get('unique_people')} people!")
                return True
            else:
                print("❌ Failed to load dataset")
                return False
                
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return False
    
    def start_recording(self, duration=8):
        """Start video recording"""
        self.print_step(3, f"Start Video Recording ({duration} seconds)")
        
        try:
            data = {
                "camera_index": 1,  # External webcam
                "duration": duration
            }
            response = requests.post(f"{self.base_url}/api/start-recording", json=data)
            result = response.json()
            self.print_result(result)
            
            if result.get("success"):
                print(f"✅ Recording started! Please look at your camera for {duration} seconds...")
                return True
            else:
                print("❌ Failed to start recording")
                return False
                
        except Exception as e:
            print(f"❌ Error starting recording: {e}")
            return False
    
    def monitor_recording(self, duration):
        """Monitor recording progress"""
        self.print_step(4, "Monitor Recording Progress")
        
        print("📹 Recording in progress...")
        for i in range(duration + 1):
            try:
                response = requests.get(f"{self.base_url}/api/recording-status")
                status = response.json()
                
                is_recording = status.get("is_recording", False)
                frames_captured = status.get("frames_captured", 0)
                
                print(f"   Time: {i:2d}s | Recording: {'🔴' if is_recording else '⚫'} | Frames: {frames_captured:3d}")
                
                if not is_recording and i > 2:  # Recording finished early
                    break
                    
                time.sleep(1)
                
            except Exception as e:
                print(f"   Error getting status: {e}")
        
        print("✅ Recording completed!")
    
    def extract_frames(self, interval=10):
        """Extract frames from recorded video"""
        self.print_step(5, f"Extract Frames (every {interval}th frame)")
        
        try:
            data = {"frame_interval": interval}
            response = requests.post(f"{self.base_url}/api/extract-frames", json=data)
            result = response.json()
            self.print_result(result)
            
            if result.get("success"):
                frames_count = len(result.get("frames", []))
                print(f"✅ Successfully extracted {frames_count} frames!")
                
                # Show some frame details
                for i, frame in enumerate(result.get("frames", [])[:5]):  # Show first 5
                    print(f"   📸 Frame {i+1}: {frame['filename']} (frame #{frame['frame_number']})")
                
                if frames_count > 5:
                    print(f"   ... and {frames_count - 5} more frames")
                
                return True
            else:
                print("❌ Failed to extract frames")
                return False
                
        except Exception as e:
            print(f"❌ Error extracting frames: {e}")
            return False
    
    def process_all_frames(self):
        """Process all frames for face recognition"""
        self.print_step(6, "Process All Frames for Face Recognition")
        
        try:
            response = requests.post(f"{self.base_url}/api/process-all-frames")
            result = response.json()
            self.print_result(result)
            
            if result.get("success"):
                total_frames = len(result.get("results", []))
                total_faces = result.get("total_faces_detected", 0)
                
                print(f"✅ Successfully processed {total_frames} frames!")
                print(f"🎯 Total faces detected: {total_faces}")
                
                # Show detection details
                print("\n📊 Detection Summary:")
                face_counts = {}
                
                for frame_result in result.get("results", []):
                    frame_name = frame_result["frame_file"]
                    faces_found = frame_result["faces_found"]
                    
                    if faces_found > 0:
                        print(f"   📸 {frame_name}: {faces_found} face(s)")
                        
                        for detection in frame_result["detections"]:
                            name = detection["name"]
                            confidence = detection["confidence"]
                            
                            if name != "Unknown":
                                face_counts[name] = face_counts.get(name, 0) + 1
                                print(f"      - {name} ({confidence:.1f}%)")
                
                # Summary by person
                if face_counts:
                    print(f"\n👥 People detected:")
                    for name, count in face_counts.items():
                        print(f"   - {name}: {count} detections")
                
                return True
            else:
                print("❌ Failed to process frames")
                return False
                
        except Exception as e:
            print(f"❌ Error processing frames: {e}")
            return False
    
    def show_results(self):
        """Show final results"""
        self.print_step(7, "View Results")
        
        frames_dir = Path("./extracted_frames")
        if frames_dir.exists():
            original_frames = list(frames_dir.glob("frame_*.jpg"))
            annotated_frames = list(frames_dir.glob("annotated_*.jpg"))
            
            print(f"📁 Results saved in: {frames_dir}")
            print(f"   📸 Original frames: {len(original_frames)}")
            print(f"   🎯 Annotated frames: {len(annotated_frames)}")
            print(f"\n💡 You can view the annotated frames to see the face detection results!")
            
            if annotated_frames:
                print(f"\n🖼️  Sample annotated frames:")
                for frame in annotated_frames[:3]:  # Show first 3
                    print(f"   - {frame.name}")
        else:
            print("❌ No results directory found")
    
    def run_complete_demo(self):
        """Run the complete demo workflow"""
        print("🚀 Face Recognition API - Complete Demo Workflow")
        print("This demo will:")
        print("1. Check API health")
        print("2. Load face recognition dataset") 
        print("3. Record video from your webcam")
        print("4. Extract frames from the video")
        print("5. Process frames for face recognition")
        print("6. Show results")
        
        input("\nPress Enter to start the demo...")
        
        # Step 1: Health check
        if not self.health_check():
            return False
        
        # Step 2: Load dataset
        if not self.load_dataset():
            return False
        
        # Step 3: Start recording
        recording_duration = 8
        if not self.start_recording(recording_duration):
            return False
        
        # Step 4: Monitor recording
        self.monitor_recording(recording_duration)
        
        # Step 5: Extract frames
        if not self.extract_frames(interval=15):  # Every 15th frame
            return False
        
        # Step 6: Process frames
        if not self.process_all_frames():
            return False
        
        # Step 7: Show results
        self.show_results()
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"✅ Your face recognition API workflow is working perfectly!")
        
        return True

def main():
    demo = FaceRecognitionDemo()
    
    print("Face Recognition API Demo")
    print("Choose an option:")
    print("1. Run complete demo workflow")
    print("2. Quick health check")
    print("3. Load dataset only")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        demo.run_complete_demo()
    elif choice == "2":
        demo.health_check()
    elif choice == "3":
        demo.health_check()
        if demo.health_check():
            demo.load_dataset()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
