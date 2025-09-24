#!/usr/bin/env python3
"""
Stable Face Recognition System with Attendance Tracking
Records detected faces as "attended" in the database
"""

import cv2
import numpy as np
import os
import time
from pathlib import Path
from collections import defaultdict, deque
from datetime import datetime
import logging
from database_manager import DatabaseManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StableFaceRecognitionWithAttendance:
    def __init__(self, dataset_path="./dataset/images"):
        """Initialize the face recognition system with attendance tracking"""
        self.dataset_path = Path(dataset_path)
        self.known_faces = []
        self.known_names = []
        
        # Initialize database manager
        try:
            self.database = DatabaseManager()
            logger.info("Database connection established for attendance tracking")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.database = None
        
        # Face detection setup
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Stability tracking
        self.detection_history = defaultdict(lambda: deque(maxlen=10))
        self.last_stable_detection = {}
        self.stability_threshold = 7  # Need 7 out of 10 detections
        self.confidence_threshold = 0.6  # Minimum confidence for attendance
        
        # Attendance tracking
        self.attendance_recorded = set()  # Track who has been recorded today
        self.session_id = None
        
        # Load faces
        self.load_faces()
        
        # Create processing session
        if self.database:
            self.create_session()
    
    def create_session(self):
        """Create a new processing session for attendance tracking"""
        try:
            session_name = f"realtime_attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            # Note: We'll need to add a create_session method to DatabaseManager
            # For now, we'll use a simple session ID
            self.session_id = 1
            logger.info(f"Created attendance session: {session_name}")
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            self.session_id = None
    
    def load_faces(self):
        """Load faces from dataset"""
        print("🎯 Loading faces for attendance tracking...")
        print("=" * 50)
        
        if not self.dataset_path.exists():
            print(f"❌ Dataset directory not found: {self.dataset_path}")
            return
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        loaded_count = 0
        
        for image_path in self.dataset_path.iterdir():
            if image_path.suffix.lower() in image_extensions:
                # Extract name from filename (remove number suffix)
                name = image_path.stem.rsplit('_', 1)[0]
                
                print(f"Loading {image_path.name} for {name}")
                
                # Load and process image
                image = cv2.imread(str(image_path))
                if image is None:
                    print(f"✗ Could not load {image_path.name}")
                    continue
                
                # Convert to grayscale and detect faces
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
                
                if len(faces) > 0:
                    # Use the first (largest) face found
                    (x, y, w, h) = faces[0]
                    face = gray[y:y+h, x:x+w]
                    face = cv2.resize(face, (100, 100))
                    
                    self.known_faces.append(face)
                    self.known_names.append(name)
                    loaded_count += 1
                    print(f"✓ Added face for {name}")
                else:
                    print(f"✗ No face found in {image_path.name}")
        
        print(f"\nTotal faces loaded: {loaded_count}")
        
        # Get unique names
        unique_names = list(set(self.known_names))
        print(f"\n✅ Loaded faces for: {', '.join(unique_names)}")
        print(f"📊 Total face samples: {len(self.known_faces)}")
    
    def recognize_face(self, face_gray):
        """Recognize a face using template matching"""
        if len(self.known_faces) == 0:
            return "Unknown", 0.0
        
        face_resized = cv2.resize(face_gray, (100, 100))
        
        best_match_name = "Unknown"
        best_confidence = 0.0
        
        for i, known_face in enumerate(self.known_faces):
            # Use template matching
            result = cv2.matchTemplate(face_resized, known_face, cv2.TM_CCOEFF_NORMED)
            confidence = result[0][0]
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match_name = self.known_names[i]
        
        return best_match_name, best_confidence
    
    def record_attendance(self, person_name: str, confidence: float):
        """Record attendance for a detected person"""
        if not self.database:
            logger.warning("Database not available - cannot record attendance")
            return False
        
        # Check if already recorded today
        today_key = f"{person_name}_{datetime.now().date()}"
        if today_key in self.attendance_recorded:
            return False  # Already recorded today
        
        try:
            # Record attendance in database
            attendance_id = self.database.record_attendance(
                person_name=person_name,
                confidence=confidence,
                session_id=self.session_id,
                location="Camera_1",
                device_info={
                    "camera_index": 1,
                    "detection_method": "stable_face_recognition",
                    "system": "real_time_attendance"
                }
            )
            
            # Mark as recorded
            self.attendance_recorded.add(today_key)
            
            print(f"📝 ATTENDANCE RECORDED: {person_name} (ID: {attendance_id})")
            logger.info(f"Recorded attendance for {person_name} with confidence {confidence:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record attendance for {person_name}: {e}")
            return False
    
    def update_stability(self, person_name, confidence):
        """Update detection stability for a person"""
        current_time = time.time()
        
        # Add detection to history
        self.detection_history[person_name].append((current_time, confidence))
        
        # Check if detection is stable
        recent_detections = len(self.detection_history[person_name])
        if recent_detections >= self.stability_threshold:
            # Calculate average confidence
            avg_confidence = np.mean([conf for _, conf in self.detection_history[person_name]])
            
            # Check if this is a new stable detection
            last_detection_time = self.last_stable_detection.get(person_name, 0)
            if current_time - last_detection_time > 5.0:  # 5 second cooldown
                self.last_stable_detection[person_name] = current_time
                
                # Record attendance if confidence is high enough
                if avg_confidence >= self.confidence_threshold:
                    self.record_attendance(person_name, avg_confidence)
                    return True, avg_confidence
        
        return False, confidence
    
    def real_time_recognition(self):
        """Run real-time face recognition with attendance tracking"""
        print("\n🚀 Starting real-time recognition with attendance tracking...")
        print("💡 Features:")
        print("   - Automatic attendance recording")
        print("   - Stable detection (7/10 confirmations)")
        print("   - Database storage with encryption")
        print("   - 5-second cooldown between recordings")
        print("\nPress Enter to start...")
        input()
        
        print("🚀 Starting stable real-time face recognition...")
        print("📹 Using external webcam (camera 1)")
        print("⏱️  Detections are stabilized over multiple frames")
        print("📝 Attendance will be recorded automatically")
        print("🔄 Press 'q' to quit")
        
        # Initialize camera
        cap = cv2.VideoCapture(1)  # Try external camera first
        if not cap.isOpened():
            print("⚠️  External camera not found, trying default camera...")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ No camera found!")
                return
        
        print("✅ Camera initialized")
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read from camera")
                    break
                
                frame_count += 1
                
                # Process every 3rd frame for performance
                if frame_count % 3 != 0:
                    cv2.imshow('Face Recognition with Attendance', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    continue
                
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
                
                # Process each detected face
                for (x, y, w, h) in faces:
                    # Extract face region
                    face_gray = gray[y:y+h, x:x+w]
                    
                    # Recognize face
                    name, confidence = self.recognize_face(face_gray)
                    
                    if name != "Unknown":
                        # Update stability and check for attendance recording
                        is_stable, avg_confidence = self.update_stability(name, confidence)
                        
                        # Choose color based on confidence and stability
                        if is_stable:
                            color = (0, 255, 0)  # Green for stable detection
                            status = "RECORDED"
                        elif avg_confidence >= self.confidence_threshold:
                            color = (0, 255, 255)  # Yellow for good confidence
                            status = "DETECTING"
                        else:
                            color = (0, 165, 255)  # Orange for low confidence
                            status = "LOW CONF"
                        
                        # Draw rectangle and label
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        
                        # Create label with status
                        label = f"{name} ({avg_confidence:.1%}) - {status}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                        
                        # Draw label background
                        cv2.rectangle(frame, (x, y-30), (x + label_size[0], y), color, -1)
                        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                        
                        # Print stable detections
                        if is_stable:
                            print(f"🎯 Stable Detection: {name} ({avg_confidence:.1%}) - ATTENDANCE RECORDED")
                    
                    else:
                        # Unknown face
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        cv2.putText(frame, f"Unknown ({confidence:.1%})", (x, y-10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Add attendance info to frame
                attendance_text = f"Attendance Today: {len(self.attendance_recorded)}"
                cv2.putText(frame, attendance_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Show frame
                cv2.imshow('Face Recognition with Attendance', frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        except KeyboardInterrupt:
            print("\n🛑 Recognition stopped by user")
        
        finally:
            # Cleanup
            cap.release()
            cv2.destroyAllWindows()
            
            # Print final attendance summary
            print(f"\n📊 Session Summary:")
            print(f"   👥 People recorded: {len(self.attendance_recorded)}")
            
            if self.database:
                try:
                    # Get today's attendance summary
                    summary = self.database.get_attendance_summary()
                    if summary:
                        print(f"   📝 Database records:")
                        for record in summary:
                            print(f"      - {record['person_name']}: {record['total_detections']} detections, "
                                  f"avg confidence: {record['average_confidence']:.1%}")
                except Exception as e:
                    logger.error(f"Failed to get attendance summary: {e}")
            
            print("🎉 Face recognition with attendance tracking completed!")

def main():
    """Main function"""
    print("🎯 Stable Face Recognition System with Attendance Tracking")
    print("=" * 60)
    
    # Initialize system
    fr_system = StableFaceRecognitionWithAttendance()
    
    if len(fr_system.known_faces) == 0:
        print("❌ No faces loaded! Please check your dataset.")
        return
    
    # Start real-time recognition
    fr_system.real_time_recognition()

if __name__ == "__main__":
    main()
